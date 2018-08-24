#!/usr/bin/env python3
from __future__ import print_function
import httplib2
import os
from os import listdir
from os.path import isfile, isdir, join
import io

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from apiclient.http import MediaFileUpload, MediaIoBaseDownload

try:
  import argparse
  flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
  flags = None

SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_id.json'
APPLICATION_NAME = 'Python OCR'

def get_credentials():
  """取得有效的憑證
     若沒有憑證，或是已儲存的憑證無效，就會自動取得新憑證

     傳回值：取得的憑證
  """
  credential_path = os.path.join("./", 'google-ocr-credential.json')
  store = Storage(credential_path)
  credentials = store.get()
  if not credentials or credentials.invalid:
    flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
    flow.user_agent = APPLICATION_NAME
    if flags:
      credentials = tools.run_flow(flow, store, flags)
    print('憑證儲存於：' + credential_path)
  return credentials

def main():

  credentials = get_credentials()
  http = credentials.authorize(httplib2.Http())
  service = discovery.build('drive', 'v3', http=http)

  files = listdir('sample')
  for f in files:
    print(f)
    imgfile = 'sample/{}'.format(f)

    txtfile = 'result/{}.txt'.format(f[:-4])

    mime = 'application/vnd.google-apps.document'
    res = service.files().create(
      body={
        'name': imgfile,
        'mimeType': mime
      },
      media_body=MediaFileUpload(imgfile, mimetype=mime, resumable=True)
    ).execute()

    downloader = MediaIoBaseDownload(
      io.FileIO(txtfile, 'wb'),
      service.files().export_media(fileId=res['id'], mimeType="text/plain")
    )
    done = False
    while done is False:
      status, done = downloader.next_chunk()

    service.files().delete(fileId=res['id']).execute()

if __name__ == '__main__':
  main()