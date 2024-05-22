import roboflow
import os
from PIL import Image
from flask import Flask, request, render_template
import base64
import io

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/start')
def start():
    return render_template('start.html')

def relocatePositions(data):
    orig_data = []
    for pred in data:
        x = float(pred['x'])
        y = float(pred['y'])
        width = float(pred['width'])
        height = float(pred['height'])
        rectangle_widthHalf = float(width/2)
        rectangle_heightHalf = float(height/2)
        x = x-rectangle_widthHalf
        y = y-rectangle_heightHalf
        prediction_data = {
            'class': pred['class'],
            'x': x,
            'y': y,
            'width': pred['width'],
            'height': pred['height']
        }
        orig_data.append(prediction_data)
    return orig_data

def setHFAttributes(data, total_height, total_width):
    updated_data = []
    header = False
    footer = False
    for pred in data:
        cls1 = pred['class']
        if cls1 == "header":
            header = True
            header_attributes = {
                'class': pred['class'],
                'x': 0,
                'y': 0,
                'width': total_width,
                'height': pred['height']
            }
            data.remove(pred)
        
        elif cls1 == "footer":
            footer = True
            footer_attributes = {
                'class': pred['class'],
                'x': 0,
                'y': pred['y'],
                'width': total_width,
                'height': pred['height']
            }
            data.remove(pred)

        else:
            updated_data.append(pred)
    if header and footer:
        return updated_data, header_attributes, footer_attributes
    elif header and not footer:
        return updated_data, header_attributes, None
    elif footer and not header:
         return updated_data, None, footer_attributes
    else:
        return updated_data, None, None
    
def setComponents(data, attr):
    header_components = []
    min_x = attr['x']
    max_x = min_x+attr['width']
    min_y = attr['y']
    max_y = min_y+attr['height']
    for preds in data:
        x = preds['x']
        y = preds['y']
        max_x2 = x+preds['width']
        max_y2 = y+preds['height']
        if (x >= min_x and x <= max_x) and (y >= min_y and y <= max_y) and (max_x2 >= min_x and max_x2 <= max_x) and (max_y2 >= min_y and max_y2 <= max_y):
            if preds not in header_components:
                header_components.append(preds)

    return header_components

def map_components(prediction):
  cls = prediction['class']
  height = prediction['height']
  width = prediction['width']
  x = prediction['x']
  y = prediction['y']
  style = f"position: absolute; left: {x}px; top: {y}px; height: {height if cls == 'navbar' and height < 50 else height}px; width: {width}px;"
  navbar_a = "float: left; display: block; color: white; text-align: center; padding: 14px 20px; text-decoration: none;"

  mapping = {
    "button": f"""
      <button class="{cls}" style="{style}">Button</button>""",
    "image": f"""
      <img src="https://www.logistec.com/wp-content/uploads/2017/12/placeholder.png" class = "{cls}" style = "{style} z-index: -2;">""",
    "navbar":f"""
      <div class="{cls}" style="{style} background-color: transparent; overflow: hidden;"><a style = "{navbar_a}" href="#home">Home</a><a style = "{navbar_a}" href="#about">About</a><a style = "{navbar_a}" href="#services">Services</a><a style = "{navbar_a}" href="#contact">Contact</a></div>""",
    "icon": f"""
      <img src="https://icons.veryicon.com/png/Media/Free%20Flat%20Multimedia/Photo.png" class = "{cls}" style = "{style}">""",
    "input": f"""
      <input class="{cls}" style="{style}" type="text" id="inputField" name="inputField">""",
    "span": f"""
      <div class="{cls}" style="{style}"><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p></div>""",
    "text-h":f"""
      <h3 class="{cls}" style="{style}">Lorem Ipsum</h3>""",
    "list": f"""
      <div class="{cls}" style="{style}"><ul><li>Item 1</li><li>Item 2</li><li>Item 3</li></ul></div>""",
    "copyright": f"""
      <div class="{cls}" style="{style}">&copy;</div>""",
    "card": f"""
      <div class="{cls}" style="{style} border-radius: 10px; box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2); background-color: #fff; padding: 20px; overflow: hidden;">
        <img src="https://via.placeholder.com/300" alt="Placeholder Image" style="width: 100%; height: 50%; border-top-left-radius: 10px; border-top-right-radius: 10px;">
        <div class="card-text" style="margin-top: 10px; font-size: 16px; line-height: 1.6; width: 100%; overflow: hidden;">
          <center>
              <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
          </center>
        </div>
      </div>""",
    "text": f"""<p class="{cls}" style="{style}">Lorem Ipsum</p>""",
    "dropdown": f"""
      <select id="dropdown" class="{cls}" style="{style}"><option value="option1">Option 1</option><option value="option2">Option 2</option><option value="option3">Option 3</option></select>""",
    "card-h":f"""
      <div class="{cls}" style="{style} border-radius: 10px; box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2); background-color: #fff; padding: 20px; overflow: hidden; display: flex; align-items: center;">
        <img src="https://via.placeholder.com/150" alt="Placeholder Image" style="width: 30%; height: 100%; border-radius: 10px; margin-right: 20px;">
        <div class="card-text" style="font-size: 16px; line-height: 1.6;">
          <center>
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
          </center>
        </div>
      </div>""",
    "date": f"""
      <div class="{cls}" id="currentDate" style="{style} font-size: 24px; font-weight: bold; text-align: center; margin: 20px; color: #000"></div>
      <script>
        var currentDate = new Date();
        var formattedDate = currentDate.toLocaleDateString('en-US', {{ month: 'long', day: 'numeric', year: 'numeric' }});
        document.getElementById('currentDate').innerText = formattedDate;
      </script>""",
    "video": f"""
      <video class="{cls}" style="{style}" controls><source src="example.mp4" type="video/mp4"></video>""",
    "textcard": f"""
      <div class="{cls}" style="{style} border-radius: 10px; box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2); background-color: #fff; padding: 20px;">
        <div class="card-text" style="margin-top: 10px; font-size: 15px; line-height: 1.6;">
          <center>
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
          </center>
        </div>
      </div>""",
    "search":f"""
      <div class="{cls}" style = "position: absolute; 300px; top: 300px; left: 400px; height: 100px; width: 103px; display: flex; align-items: center;" >
        <input type="text" class="search-input" placeholder="Enter your search term">
        <button>Search</button>
      </div>""",
    "form": f"""
    <form class="{cls}" style="{style}"><label for="fname">First name:</label><br><input type="text" id="fname" name="fname"><br><label for="lname">Last name:</label><br><input type="text" id="lname" name="lname"></form>""",
    "link": f"""
    <div class="{cls}" style="{style}"><p><a href="https://www.example.com">link</a></p></div>""",
    "googlemap":f"""
    <iframe class ="{cls}" style = "{style} border:0" frameborder="0" src="https://www.google.com/maps/embed/v1/view?key=YOUR_API_KEY&center=latitude,longitude&zoom=15" allowfullscreen></iframe>"""
  }
  if cls in mapping:
    return mapping[cls]
  
def yieldResult(header_output, main_output, footer_output, header_attr, footer_attr, hasHeader, hasFooter, color1 = "#A0A2A4", color2 = "#E0E1E0", color3 = "#C0C2C4"):
  if hasHeader: header_height = header_attr['height']
  if hasFooter: 
    footer_y = footer_attr['y']
    footer_height = footer_attr['height']
  # @title Generate Template
  if hasHeader: header_style= f"position: absolute; left: 0; top: 0; height:{header_height}px; background-color: {color1}; color: #fff; padding: 10px 20px; width: 100%; z-index:-1;"
  if hasFooter: footer_style= f"position: absolute; top: {footer_y}px; height:{footer_height}px; background-color: {color3}; color: #fff; padding: 10px 20px; width: 100%; z-index:-1;"

  final_result =f"""<!DOCTYPE html>
  <html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Snap2Site Webpage</title>
    <style>
      body {{
        margin: 0;
        padding: 0;
        height: 100%;
        background-color: {color2};
      }}

      .container {{
        position: relative;
        min-height: 100%;
      }}
    </style>
  </head>
  <body>
  {f'<header style="{header_style}">{header_output}</header>' if hasHeader else ''}
  <div class="container">
  {main_output}
  </div>
  {f'<footer style="{footer_style}">{footer_output}</footer>' if hasFooter else ''}
  </body>
  </html>"""
  return final_result

def processImage(image):
    total_width= 0
    total_height =0
    with Image.open(image) as img:
        total_width, total_height = img.size
    rf = roboflow.Roboflow(api_key='5LsoBZbeCzCMrmYFxZeH')
    project = rf.workspace().project("test-vnnxn")
    model = project.version(2).model
    result = model.predict(image, confidence=30, overlap=1).json()
    orig_data = []
    main_components = []
    hasHeader = False
    hasFooter = False
    for prediction in result['predictions']:
        prediction_data = {
            'class': prediction['class'],
            'x': prediction['x'],
            'y': prediction['y'],
            'width': prediction['width'],
            'height': prediction['height']
        }
        if prediction['class'] == "header":
            hasHeader = True
        if prediction['class'] == "footer":
            hasFooter = True
        orig_data.append(prediction_data)
    data = relocatePositions(orig_data)
    data, header_attr, footer_attr = setHFAttributes(data,total_height,total_width)
    header_components = []
    footer_components = []
    if hasHeader: header_components = setComponents(data, header_attr)
    if hasFooter: footer_components = setComponents(data, footer_attr)
    if hasHeader or hasFooter: main_components = [preds for preds in data if preds not in header_components and preds not in footer_components] 
    else: main_components = data
    header_output = []
    main_output = []
    footer_output = []
    if hasHeader:
        for prediction in header_components:
            header_output.append(map_components(prediction))
    if hasFooter:
        for prediction in footer_components:
            footer_output.append(map_components(prediction))
    for prediction in main_components:
        main_output.append(map_components(prediction))
    header_output = '\n'.join(header_output)
    main_output = '\n'.join(main_output)
    footer_output = '\n'.join(footer_output)
    return yieldResult(header_output, main_output, footer_output, header_attr, footer_attr, hasHeader, hasFooter)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/generate', methods=['POST'])
def generate():
    # Get the base64 image data from the form
    image_data_base64 = request.form['image_data']
    # Remove the data URL prefix
    image_data_base64 = image_data_base64.replace('data:image/png;base64,', '')

    # Convert base64 data to binary
    image_data_binary = base64.b64decode(image_data_base64)

    # Save the image to a file
    image_path = os.path.join(UPLOAD_FOLDER, 'uploaded_image.png')
    with open(image_path, 'wb') as f:
        f.write(image_data_binary)

    # Now you can proceed with processing the image data as needed
    result = processImage(image_path)  # Example function for processing the image
    return render_template('generate.html', result=result)


if __name__ == '__main__':
    app.run(debug=True)
