from html2image import Html2Image
import os

class HTMLRenderer:
        def __init__(self):
            self.html = ""
            self.template = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
              <meta charset="UTF-8">
              <meta name="viewport" content="width=device-width, initial-scale=1.0">
              <title>PowerPoint Style Slide</title>
              <style>
                body {{
                  font-family: 'Arial', sans-serif;
                  margin: 0;
                  padding: 0;
                  background: linear-gradient(135deg, #e3f2fd, #ffffff);
                  display: flex;
                  justify-content: center;
                  align-items: center;
                  height: 100vh;
                  width: 100vw;
                  color: #333;
                }}
                .slide {{
                  width: 100%;
                  height: 100%;
                  background: #ffffff;
                  border-radius: 12px;
                  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
                  padding: 5%;
                  box-sizing: border-box;
                  display: flex;
                  flex-direction: column;
                  justify-content: space-between;
                }}
                .slide-title {{
                  font-size: 3em; /* Adjust font size to scale dynamically */
                  margin-bottom: 20px;
                  text-align: center;
                  color: #0077cc;
                  font-weight: bold;
                }}
                .content {{
                  display: flex;
                  justify-content: space-between;
                  align-items: flex-start;
                  flex: 1;
                }}
                .bullet-points {{
                  width: 58%;
                  list-style-type: disc;
                  padding-left: 30px;
                  font-size: 1.5em; /* Adjust font size */
                  line-height: 1.8;
                  color: #555;
                }}
                .bullet-points li {{
                  margin-bottom: 10px;
                }}
                .image-container {{
                  width: 38%;
                  display: flex;
                  justify-content: center;
                  align-items: center;
                  border: 2px solid #ddd;
                  border-radius: 8px;
                  background-color: #f0f4f8;
                  padding: 10px;
                  box-sizing: border-box;
                }}
                .image-container img {{
                  max-width: 100%;
                  max-height: 100%;
                  border-radius: 6px;
                }}
              </style>
            </head>
            <body>
              <div class="slide">
                <div class="slide-title">{title}</div>
                <div class="content">
                  <ul class="bullet-points">
                    {bullet_points}
                  </ul>
                  <div class="image-container">
                    <img src="{image_url}" alt="Slide Image">
                  </div>
                </div>
              </div>
            </body>
            </html>
            """

        def generate_slide(self, title, bullet_points, image_url):
            """
            Generate the HTML for a slide.

            :param title: The title of the slide.
            :param bullet_points: A list of bullet points.
            :param image_url: URL or path of the image to display.
            :return: A string containing the complete HTML template for the slide.
            """
            bullet_points_html = "".join(f"<li>{point}</li>" for point in bullet_points)
            self.html = self.template.format(title=title, bullet_points=bullet_points_html, image_url=image_url)

        def render_slide(self, output_path):
            hti = Html2Image()

            custom_size = (1920, 1080)

            if os.path.isfile(self.html):
                hti.screenshot(url_or_file=self.html, save_as=output_path, size=custom_size)
            else:
                hti.screenshot(html_str=self.html, save_as=output_path, size=custom_size)

if __name__ == "__main__":
    generator = HTMLRenderer()
    slide_title = "Dynamic Slide Example"
    slide_bullets = ["Bullet point 1", "Bullet point 2", "Bullet point 3", "Bullet point 4", "Aaaaaaaa"]
    slide_image_url = "https://via.placeholder.com/150"

    generator.generate_slide(slide_title, slide_bullets, slide_image_url)
    generator.render_slide("slide.png")
