from html2image import Html2Image
import os

class SlideRenderer:
    def __init__(self, templates_dir="templates"):
        """
        Initialize with the directory where templates are stored.
        """
        self.templates_dir = templates_dir
        self.html = ""

    def load_template(self, template_name):
        """
        Load an HTML template file.
        :param template_name: The name of the template file (e.g., "intro.html").
        :return: The template as a string.
        """
        file_path = os.path.join(self.templates_dir, template_name)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Template {template_name} not found in {self.templates_dir}")
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()

    def generate_intro_slide(self, title, subtitle, template_name="intro.html"):
        """
        Generate an introduction slide with a title and subtitle.
        :param title: The title of the slide.
        :param subtitle: The subtitle of the slide.
        :param template_name: The template name for the intro slide.
        """
        template = self.load_template(template_name)
        self.html = template.replace("{{ title }}", title).replace("{{ subtitle }}", subtitle)

    def generate_main_slide(self, title, bullet_points=None, image_url="", template_name="main1.html"):
        """
        Generate a main presentation slide with a title, bullet points, and an image.
        :param title: The title of the slide.
        :param bullet_points: A list of bullet points (optional).
        :param image_url: The URL or path of the image to display (optional).
        :param template_name: The template name for the main slide.
        """
        template = self.load_template(template_name)
        bullet_points_html = ""
        if bullet_points:
            bullet_points_html = "".join(f"<li>{point}</li>" for point in bullet_points)
        self.html = template.replace("{{ title }}", title)
        self.html = self.html.replace("{{ bullet_points }}", bullet_points_html)
        self.html = self.html.replace("{{ image_url }}", image_url)

    def generate_conclusion_slide(self, thank_you, call_to_action, template_name="conclusion.html"):
        """
        Generate a conclusion slide with a thank-you message and a call-to-action.
        :param thank_you: The thank-you message for the slide.
        :param call_to_action: The call-to-action text for the slide.
        :param template_name: The template name for the conclusion slide.
        """
        template = self.load_template(template_name)
        self.html = template.replace("{{ thank_you }}", thank_you).replace("{{ call_to_action }}", call_to_action)

    def render_slide(self, output_path, size=(1920, 1080)):
        """
        Render the HTML slide to an image.
        :param output_path: Path to save the rendered image.
        :param size: Tuple specifying the width and height of the rendered image.
        """
        hti = Html2Image()
        hti.screenshot(html_str=self.html, save_as=output_path, size=size)

if __name__ == "__main__":
    # Example usage
    generator = SlideRenderer()

    # Slide 1: Introduction slide
    intro_title = "Welcome to the Presentation"
    intro_subtitle = "Let's Begin with Exciting Topics"
    generator.generate_intro_slide(title=intro_title, subtitle=intro_subtitle, template_name="intro.html")
    generator.render_slide("intro_slide.png")

    # Slide 2: Main content slide
    slide_title = "Dynamic Slide Example"
    slide_bullets = ["Bullet point 1", "Bullet point 2", "Bullet point 3", "Bullet point 4"]
    slide_image_url = "videos/blockchain.png"
    generator.generate_main_slide(title=slide_title, bullet_points=slide_bullets, image_url=slide_image_url,
                                  template_name="slide_2.html")
    generator.render_slide("main_slide.png")

    # Slide 3: Conclusion slide
    conclusion_thank_you = "Thank You for Your Attention!"
    conclusion_cta = "Feel free to ask questions or reach out!"
    generator.generate_conclusion_slide(thank_you=conclusion_thank_you, call_to_action=conclusion_cta,
                                        template_name="conclusion.html")
    generator.render_slide("conclusion_slide.png")
