from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips

class PresentationBuilder:
    def __init__(self, video_position=("right", "bottom"), video_size=(100, None)):
        """
        Initializes the PresentationBuilder with default parameters.

        :param video_position: Position of the overlaid video on the slide.
        :param video_size: Size to which the overlaid video should be resized (width, height).
                           Use None to maintain aspect ratio.
        """
        self.slides = []
        self.video_position = video_position
        self.video_size = video_size

    def add_slide(self, image_path, video_path=None):
        """
        Adds a slide to the presentation.

        :param image_path: Path to the slide image.
        :param video_path: Path to the video to overlay on the slide (optional).
        """
        # Load the slide image
        slide = ImageClip(image_path)

        if video_path:
            # Load the video clip
            video_clip = VideoFileClip(video_path)

            # Resize the video
            video_resized = video_clip.resize(height=self.video_size[1], width=self.video_size[0])

            # Set video position
            video_positioned = video_resized.set_position(self.video_position)

            # Set slide duration to match video duration
            slide = slide.set_duration(video_clip.duration)

            # Create composite video
            slide = CompositeVideoClip([slide, video_positioned])

            # Set audio
            slide = slide.set_audio(video_clip.audio)
        else:
            # If no video, set a default duration
            slide = slide.set_duration(5)  # Default duration in seconds

        self.slides.append(slide)

    def produce_presentation(self, output_path, fps=24):
        """
        Produces the final presentation video by concatenating all slides.

        :param output_path: Path to save the final video.
        :param fps: Frames per second for the output video.
        """
        if not self.slides:
            raise ValueError("No slides have been added to the presentation.")

        # Concatenate all slides
        final_clip = concatenate_videoclips(self.slides, method="compose")

        # Write the final video file
        final_clip.write_videofile(
            output_path,
            fps=fps,
            codec='libx264',  # Video codec
            audio_codec='aac',  # Audio codec
            temp_audiofile='temp-audio.m4a',  # Temporary audio file
            remove_temp=True  # Remove temporary files after completion
        )

if __name__ == "__main__":
    # Initialize the presentation builder
    presentation = PresentationBuilder(
        video_position=("right", "bottom"),
        video_size=(400, None)
    )

    # Add slides with optional video overlays
    presentation.add_slide("slide.png", "videos/john-china.mp4")

    # Produce the final presentation video
    presentation.produce_presentation("videos/out.mp4", fps=24)
