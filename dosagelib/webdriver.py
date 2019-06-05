#Webdriver file
import sys
import os
import platform
import requests
import time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException

from .output import out
from .configuration import UserAgent

retryDelay = 30
tryMax = 3
driver = None
seleniumUse = True
driverbackup = False

class ResponseMimic:
  #mimic response object
  out.debug(u'Getting metadata')
  def __init__(self, content, resp):
    #Get real headers from urllib request
    self.encoding = resp.encoding
    self.headers = resp.headers
    self.status_code= resp.status_code
    try:
      self.json=resp.json()
    except:
      self.json=None
    #Add to data from webdriver
    self.content = content
    self.text = content

def startDriver():
  sys = platform.system()
  if sys == 'Windows':
    driverProgram = '\chromedriver_win32.exe'
  elif sys == 'Darwin':
    #check correct
    driverProgram = '\chromedriver_mac64'
  elif sys == 'Linux':
    driverProgram = '\chromedriver_linux64'
  else:
    raise Exception('Unidentifed system type by platform.system()')

  #Chrome must be installed in default location
  driverPath =os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)),os.pardir))  + '\dosagelib\chromedriver' +driverProgram
  optionsC = webdriver.ChromeOptions()
  optionsC.add_argument('--headless')
  optionsC.add_argument('--log-level=3')
  optionsC.add_argument('--disable-gpu')
  """This will only disable devtools listenings messages if and only if you followed the steps at 
  https://stackoverflow.com/questions/48654427/hide-command-prompt-in-selenium-chromedriver?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
  to edit the selenium library"""
  args = ["hide_console", ]
  global driver
  driver = webdriver.Chrome(chrome_options=optionsC, executable_path=driverPath, service_args=args)
  driver.set_page_load_timeout(30)
  out.debug(u'Chrome Headless Browser Invoked')

def getPageDataSel(url):
  trys =1

  while (trys <= tryMax):
    #get page content
    try:
      time.sleep(5+retryDelay**(trys-1))
      out.debug(u'Navigating to page. Establishing connection, try %s of %s' % (trys, tryMax))
      try:
        driver.get(url)
      except AttributeError:
        startDriver()
        driver.get(url)
      source =driver.page_source
      break
    except Exception as e:
      driver.quit()
      if (trys == tryMax):
        out.error(u'Connection failed: Max retrys reached' +str(e))
        source = u'0'
        break
      else:
        out.warn(u'Connection error: Retrying with delay')
        trys = trys+1

  #get page metadata
  try:
    headersReq = {}
    headersReq['User-Agent'] = UserAgent
    resp = requests.get(url, headers = headersReq)
  except requests.exceptions.RequestException as err:
    msg = 'URL retrieval of %s failed: %s' % (url, err)
    raise IOError(msg)


  page = ResponseMimic(source, resp)

  return page

def getImgDataSel(url):
  trys = 1

  #get img content
  while (trys <= tryMax):
    try:
      time.sleep(retryDelay**(trys-1))
      out.debug(u'Navigating to image. Establishing connection, try %s of %s' % (trys, tryMax))
      try:
        driver.get(url)
      except AttributeError:
        startDriver()
        driver.get(url)

      orig_h = driver.execute_script("return window.outerHeight")
      orig_w = driver.execute_script("return window.outerWidth")
      
      # Get the dimensions of the browser and image.
      driver.set_window_size(2000, 6500)
      o_h = driver.execute_script("return window.outerHeight")
      o_w = driver.execute_script("return window.outerWidth")
      margin_h = o_h - driver.execute_script("return window.innerHeight")
      margin_w = o_w - driver.execute_script("return window.innerWidth")
      new_h = driver.execute_script('return document.getElementsByTagName("img")[0].height')
      new_w = driver.execute_script('return document.getElementsByTagName("img")[0].width')

      # Resize the browser window.
      driver.set_window_size(new_w + margin_w, new_h + margin_h)

      # Get the image by taking a screenshot of the page.
      img = driver.get_screenshot_as_png()
      # Set the window size back to what it was.
      driver.set_window_size(orig_w, orig_h)

      break

    except:
      driver.quit()
      if (trys == tryMax):
        out.error(u'Connection failed: Max retrys reached')
        raise
      else:
        out.warn(u'Connection error: Retrying with delay')
        trys = trys+1

  return img

def exitDrivers():
  out.debug(u'Exiting Chrome Headless Browser')
  try:
    driver.quit()
  except Exception as e:
    out.error(u'Error quitting driver' + str(e))