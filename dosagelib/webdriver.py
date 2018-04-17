#Webdriver file
import sys
import os
from selenium import webdriver
from selenium.common.exceptions import TimeoutException

from .output import out

driver = None
seleniumUse = True
driverbackup = False

class ResponseMimic:
  #mimic response object
  def __init__(self, content, text):
    self.content = content
    self.text = text
    self.encoding = None
    self.headers = {}
    self.headers['content-encoding'] = "image/"
    self.status_code= 200

def startDriver():
  driverPath =os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)),os.pardir))  + '\scripts\chromedriver.exe'
  optionsC = webdriver.ChromeOptions()
  optionsC.add_argument('headless')
  optionsC.add_argument('--log-level=3')
  args = ["hide_console", ]
  global driver
  driver = webdriver.Chrome(chrome_options=optionsC, executable_path=driverPath, service_args=args)
  driver.set_page_load_timeout(30)
  out.debug(u'Chrome Headless Browser Invoked')

def getPageDataSel(url):
  out.debug(u'Navigating to page')
  startDriver()

  try:
    driver.get(url)
  except Exception as ex:
    out.warn(u'Retrying. Exception: '+ str(ex))
    try:
      driver.quit()
      startDriver()
      driver.get(url)
    except:
      raise

  content = driver.page_source
  text = driver.page_source
  page = ResponseMimic(content, text)

  out.debug(u'Exiting Chrome Headless Browser')
  driver.quit()
  return page

def getImgDataSel(url):
  out.debug(u'Navigating to image')

  try:
    driver.get(url)
  except Exception as ex:
    out.warn(u'Retrying. Exception: '+ str(ex))
    try:
      driver.quit()
      startDriver()
      driver.get(url)
    except:
      raise

  driver.set_window_size(2000, 2000)
    
  # Get the dimensions of the browser and image.
  orig_h = driver.execute_script("return window.outerHeight")
  orig_w = driver.execute_script("return window.outerWidth")
  margin_h = orig_h - driver.execute_script("return window.innerHeight")
  margin_w = orig_w - driver.execute_script("return window.innerWidth")
  new_h = driver.execute_script('return document.getElementsByTagName("img")[0].height')
  new_w = driver.execute_script('return document.getElementsByTagName("img")[0].width')

  # Resize the browser window.
  driver.set_window_size(new_w + margin_w, new_h + margin_h)

  # Get the image by taking a screenshot of the page.
  img = driver.get_screenshot_as_png()
  # Set the window size back to what it was.
  driver.set_window_size(orig_w, orig_h)
  out.debug(u'Exiting Chrome Headless Browser')
  driver.quit()
  return img
