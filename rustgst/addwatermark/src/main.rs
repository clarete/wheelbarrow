use std::path::Path;

#[macro_use]
extern crate log;
#[macro_use]
extern crate anyhow;
use anyhow::Error;
use gdk_pixbuf;
use gst::{self, prelude::*};
use glib::object::WeakRef;
extern crate gstreamer_pbutils as gst_pbutils;

use gst_pbutils::prelude::*;

/// Build the output file name based on the input URI
fn output_file_name(input: &str) -> Result<String, Error> {
    // Get the output file name
    let path = Path::new(input);
    let (file, ext) = (path.file_stem(), path.extension());
    if file.is_none() {
        bail!("Input file can't be a directory");
    }
    let file = file.unwrap().to_string_lossy();
    let output_file = match ext {
        Some(ext) => format!("{}.watermark.{}", file, ext.to_string_lossy()),
        None => format!("{}.watermark", file),
    };
    Ok(output_file)
}

/// Load Gstreamer element with a nice error message containing the
/// element name in case of failure
fn make_element(name: &str, id: Option<&str>) -> Result<gst::Element, Error> {
    Ok(
        gst::ElementFactory::make(name, id)
            .map_err(|_| anyhow!("Can't load element {}", name))?,
    )
}

fn configure_source(pipeline_weak: WeakRef<gst::Pipeline>, src: &gst::Element) {
    src.connect_pad_added(move |_dbin, dbin_src_pad| {
        // Here we temporarily retrieve a strong reference on the
        // pipeline from the weak one we moved into this callback.
        let pipeline = match pipeline_weak.upgrade() {
            Some(pipeline) => pipeline,
            None => return,
        };

        let encodebin = match pipeline.get_by_name("encode") {
            Some(encodebin) => encodebin,
            None => return,
        };

        let (is_audio, is_video) = {
            let media_type = dbin_src_pad.get_current_caps().and_then(|caps| {
                caps.get_structure(0).map(|s| {
                    let name = s.get_name();
                    (name.starts_with("audio/"), name.starts_with("video/"))
                })
            });

            match media_type {
                None => {
                    warn!(
                        "Failed to get media type from pad {}",
                        dbin_src_pad.get_name()
                    );

                    return;
                }
                Some(media_type) => media_type,
            }
        };

        let link_to_encodebin = |is_audio, is_video| -> Result<(), Error> {
            if is_audio {
                let queue = make_element("queue", None)?;
                let convert = make_element("audioconvert", None)?;
                let resample = make_element("audioresample", None)?;
                let elements = &[&queue, &convert, &resample];
                pipeline
                    .add_many(elements)
                    .expect("failed to add audio elements to pipeline");
                gst::Element::link_many(elements)?;

                // Request a sink pad from our encodebin, that can
                // handle a raw audiostream.  The encodebin will then
                // automatically create an internal pipeline, that
                // encodes the audio stream in the format we specified
                // in the EncodingProfile.
                let enc_sink_pad = encodebin
                    .get_request_pad("audio_%u")
                    .expect("Could not get audio pad from encodebin");
                let src_pad = resample
                    .get_static_pad("src")
                    .expect("resample has no srcpad");
                src_pad.link(&enc_sink_pad)?;

                for e in elements {
                    e.sync_state_with_parent()?;
                }

                // Get the queue element's sink pad and link the decodebin's newly created
                // src pad for the audio stream to it.
                let sink_pad = queue.get_static_pad("sink").expect("queue has no sinkpad");
                dbin_src_pad.link(&sink_pad)?;
            } else if is_video {
                let queue = make_element("queue", None)?;
                let convert = make_element("videoconvert", None)?;
                let scale = make_element("videoscale", None)?;
                let elements = &[&queue, &convert, &scale];
                pipeline
                    .add_many(elements)
                    .expect("failed to add video elements to pipeline");
                gst::Element::link_many(elements)?;

                // Request a sink pad from our encodebin, that can
                // handle a raw videostream.  The encodebin will then
                // automatically create an internal pipeline, that
                // encodes the audio stream in the format we specified
                // in the EncodingProfile.
                let enc_sink_pad = encodebin
                    .get_request_pad("video_%u")
                    .expect("Could not get video pad from encodebin");
                let src_pad = scale
                    .get_static_pad("src")
                    .expect("videoscale has no srcpad");
                src_pad.link(&enc_sink_pad)?;

                for e in elements {
                    e.sync_state_with_parent()?
                }

                // Get the queue element's sink pad and link the
                // decodebin's newly created src pad for the video
                // stream to it.
                let sink_pad = queue.get_static_pad("sink").expect("queue has no sinkpad");
                dbin_src_pad.link(&sink_pad)?;
            }

            Ok(())
        };

        info!("is_audio: {}, is_video: {}", is_audio, is_video);

        if let Err(err) = link_to_encodebin(is_audio, is_video) {
            error!("Failed to insert sink {}", err);
        }
    });
}

fn configure_encoder(encodebin: &gst::Element) -> Result<(), Error> {
    // To tell the encodebin what we want it to produce, we create an
    // EncodingProfile
    // https://gstreamer.freedesktop.org/data/doc/gstreamer/head/gst-plugins-base-libs/html/GstEncodingProfile.html
    // This profile consists of information about the contained audio
    // and video formats as well as the container format we want
    // everything to be combined into.

    // Every audiostream piped into the encodebin should be encoded using vorbis.
    let audio_profile = gst_pbutils::EncodingAudioProfileBuilder::new()
        .format(&gst::Caps::new_simple("audio/x-vorbis", &[]))
        .presence(0)
        .build()?;

    // Every videostream piped into the encodebin should be encoded using theora.
    let video_profile = gst_pbutils::EncodingVideoProfileBuilder::new()
        .format(&gst::Caps::new_simple("video/x-theora", &[]))
        .presence(0)
        .build()?;

    // All streams are then finally combined into a matroska container.
    let container_profile = gst_pbutils::EncodingContainerProfileBuilder::new()
        .name("container")
        .format(&gst::Caps::new_simple("video/x-matroska", &[]))
        .add_profile(&(video_profile))
        .add_profile(&(audio_profile))
        .build()?;

    // Finally, apply the EncodingProfile onto our encodebin element.
    encodebin
        .set_property("profile", &container_profile)
        .expect("set profile property failed");

    Ok(())
}

/// Build the pipeline and run it
fn execute(video_uri: &str, image_uri: &str) -> Result<(), Error> {
    gst::init()?;

    // Build the pipeline
    let pipeline = gst::Pipeline::new(None);
    let src = make_element("uridecodebin", Some("src"))?;
    let encodebin = make_element("encodebin", Some("encode"))?;
    let sink = make_element("filesink", None)?;
    let overlay = make_element("gdkpixbufoverlay", None)?;

    let output_file = output_file_name(video_uri)?;
    src.set_property("uri", &video_uri)?;
    sink.set_property("location", &output_file)?;

    let watermark = gdk_pixbuf::Pixbuf::new_from_file(Path::new(image_uri))?;
    overlay.set_property("pixbuf", &watermark)?;
    // overlay.set_property("positioning-mode", &1)?;

    configure_encoder(&encodebin)?;

    pipeline.add_many(&[&src, &encodebin, &sink])?;

    gst::Element::link_many(&[&encodebin, &sink])?;

    configure_source(pipeline.downgrade(), &src);

    pipeline.set_state(gst::State::Playing)?;

    let bus = pipeline
        .get_bus()
        .expect("Pipeline without bus. Shouldn't happen!");

    for msg in bus.iter_timed(gst::CLOCK_TIME_NONE) {
        use gst::MessageView;

        match msg.view() {
            MessageView::Eos(..) => break,
            MessageView::Error(err) => {
                pipeline.set_state(gst::State::Null)?;

                error!("ERROR: {:?} {}", err, msg
                       .get_src()
                       .map(|s| String::from(s.get_path_string()))
                       .unwrap_or_else(|| String::from("None")));
            }
            MessageView::StateChanged(s) => {
                println!(
                    "State changed from {:?}: {:?} -> {:?} ({:?})",
                    s.get_src().map(|s| s.get_path_string()),
                    s.get_old(),
                    s.get_current(),
                    s.get_pending()
                );
            }
            _ => (),
        }
    }

    pipeline.set_state(gst::State::Null)?;

    Ok(())
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() != 3 {
        println!("Usage: {} VIDEO-FILE IMAGE-FILE", args[0]);
    }
    if let Err(e) = execute(&args[1], &args[2]) {
        println!("Error: {}", e);
    }
}
