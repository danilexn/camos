from PyQt5 import QtCore

# SVG icons
chevron_down_svg = b"""<?xml version="1.0" encoding="utf-8"?>
<!-- Generator: Adobe Illustrator 23.0.1, SVG Export Plug-In . SVG Version: 6.00 Build 0)  -->
<svg version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px"
	 viewBox="0 0 100 100" style="enable-background:new 0 0 100 100;" xml:space="preserve">
<path d="M51.3,75.9c-1.9,0-3.8-0.8-5-2.4L18.1,38.4c-2.2-2.8-1.8-6.9,1-9.1c2.8-2.2,6.9-1.8,9.1,1l28.2,35.1c2.2,2.8,1.8,6.9-1,9.1
	C54.2,75.5,52.7,75.9,51.3,75.9z"/>
<path d="M51.3,75.9c-1.4,0-2.9-0.5-4-1.4c-2.8-2.2-3.2-6.3-1-9.1l28.2-35.1c2.2-2.8,6.3-3.2,9.1-1c2.8,2.2,3.2,6.3,1,9.1L56.4,73.5
	C55.1,75.1,53.2,75.9,51.3,75.9z"/>
</svg>"""

chevron_down_svg_file = QtCore.QTemporaryFile()
if chevron_down_svg_file.open():
    chevron_down_svg_file.write(chevron_down_svg)
    chevron_down_svg_file.flush()

chevron_up_svg = b"""<?xml version="1.0" encoding="utf-8"?>
<!-- Generator: Adobe Illustrator 23.0.1, SVG Export Plug-In . SVG Version: 6.00 Build 0)  -->
<svg version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px"
	 viewBox="0 0 100 100" style="enable-background:new 0 0 100 100;" xml:space="preserve">
<path d="M51.4,27.9c1.9,0,3.8,0.8,5,2.4l28.2,35.1c2.2,2.8,1.8,6.9-1,9.1c-2.8,2.2-6.9,1.8-9.1-1L46.3,38.4c-2.2-2.8-1.8-6.9,1-9.1
	C48.5,28.3,50,27.9,51.4,27.9z"/>
<path d="M51.4,27.9c1.4,0,2.9,0.5,4,1.4c2.8,2.2,3.2,6.3,1,9.1L28.2,73.5c-2.2,2.8-6.3,3.2-9.1,1c-2.8-2.2-3.2-6.3-1-9.1l28.2-35.1
	C47.6,28.7,49.5,27.9,51.4,27.9z"/>
</svg>"""

chevron_up_svg_file = QtCore.QTemporaryFile()
if chevron_up_svg_file.open():
    chevron_up_svg_file.write(chevron_up_svg)
    chevron_up_svg_file.flush()

delete_shape_svg = b"""<?xml version="1.0" encoding="utf-8"?>
<!-- Generator: Adobe Illustrator 23.0.1, SVG Export Plug-In . SVG Version: 6.00 Build 0)  -->
<svg version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px"
	 viewBox="0 0 100 100" style="enable-background:new 0 0 100 100;" xml:space="preserve">
<rect x="45" y="21.3" transform="matrix(0.7112 -0.7029 0.7029 0.7112 -21.6791 50.024)" width="10" height="60.2"/>
<rect x="19.9" y="46.4" transform="matrix(0.7113 -0.7029 0.7029 0.7113 -21.7284 49.9988)" width="60.2" height="10"/>
</svg>"""

delete_shape_svg_file = QtCore.QTemporaryFile()
if delete_shape_svg_file.open():
    delete_shape_svg_file.write(delete_shape_svg)
    delete_shape_svg_file.flush()

# Styles (QSS)
notification_style = (
    """
CaMOSQtNotification > QWidget {
  background: #303030;
}

CaMOSQtNotification::hover{
  background: {{ lighten(background, 5) }};
}

MultilineElidedLabel{
  background: none;
  color: {{ icon }};
  font-size: 12px;
}

CaMOSQtNotification #expand_button {
  background: none;
  padding: 0px;
  margin: 0px;
  max-width: 20px;
}

CaMOSQtNotification[expanded="false"] #expand_button {
  image: url("""
    + chevron_up_svg_file.fileName()
    + """);
}

CaMOSQtNotification[expanded="true"] #expand_button {
  image: url("""
    + chevron_down_svg_file.fileName()
    + """);
}


CaMOSQtNotification #close_button {
  background: none;
  image: url("""
    + delete_shape_svg_file.fileName()
    + """);
  padding: 0px;
  margin: 0px;
  max-width: 20px;
}

CaMOSQtNotification #source_label {
  color: {{ primary }};
  font-size: 11px;
}

CaMOSQtNotification #severity_icon {
  padding: 0;
  margin: 0 0 -3px 0;
  min-width: 20px;
  min-height: 18px;
  font-size: 15px;
  color: {{ icon }};
}
"""
)
