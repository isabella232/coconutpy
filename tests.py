import unittest
import coconut
from coconut import job, config
import os
import time

API_KEY_PARAM = None

class CoconutTestCase(unittest.TestCase):
    @unittest.skipIf(API_KEY_PARAM is None,
                   'To run this test, set API_KEY_PARAM, but do not commit it to the repo.')
    def test_submit_job(self):
      conf = coconut.config.new(
        source='https://s3-eu-west-1.amazonaws.com/files.coconut.co/test.mp4',
        webhook='http://mysite.com/webhook',
        outputs={'mp4': 's3://a:s@bucket/video.mp4'}
      )

      job = coconut.job.submit(conf)
      self.assertEqual("processing", job["status"])
      self.assertTrue(job["id"] > 0)

    @unittest.skipIf(API_KEY_PARAM is None, 
                     'To run this test, set API_KEY_PARAM, but do not commit it to the repo.')
    def test_submit_job_with_auth_token_param(self):
      conf = coconut.config.new(
        source='https://s3-eu-west-1.amazonaws.com/files.coconut.co/test.mp4',
        webhook='http://mysite.com/webhook',
        outputs={'mp4': 's3://a:s@bucket/video.mp4'}
      )

      job = coconut.job.submit(conf, api_key=API_KEY_PARAM)
      self.assertEqual("processing", job["status"])
      self.assertTrue(job["id"] > 0)

    def test_submit_bad_config(self):
      conf = coconut.config.new(
        source='https://s3-eu-west-1.amazonaws.com/files.coconut.co/test.mp4'
      )

      job = coconut.job.submit(conf)
      self.assertEqual("error", job["status"])
      self.assertEqual("config_not_valid", job["error_code"])

    def test_generate_full_config_with_no_file(self):
      conf = coconut.config.new(
        vars={
          'vid': 1234,
          'user': 5098,
          's3': 's3://a:s@bucket'
        },
        source='https://s3-eu-west-1.amazonaws.com/files.coconut.co/test.mp4',
        webhook='http://mysite.com/webhook?vid=$vid&user=$user',
        outputs={
          'mp4': '$s3/vid.mp4',
          'webm': '$s3/vid.webm',
          'jpg_200x': '$s3/thumb.jpg'
        }
      )

      generated = "\n".join([
        'var s3 = s3://a:s@bucket',
        'var user = 5098',
        'var vid = 1234',
        '',
        'set source = https://s3-eu-west-1.amazonaws.com/files.coconut.co/test.mp4',
        'set webhook = http://mysite.com/webhook?vid=$vid&user=$user',
        '',
        '-> jpg_200x = $s3/thumb.jpg',
        '-> mp4 = $s3/vid.mp4',
        '-> webm = $s3/vid.webm'
      ])

      self.assertEqual(generated, conf)

    def test_generate_config_with_file(self):
      file = open('coconut.conf', 'w')
      file.write("var s3 = s3://a:s@bucket/video\nset webhook = http://mysite.com/webhook?vid=$vid&user=$user\n-> mp4 = $s3/$vid.mp4")
      file.close()

      conf = coconut.config.new(
        conf='coconut.conf',
        source='https://s3-eu-west-1.amazonaws.com/files.coconut.co/test.mp4',
        vars={'vid': 1234, 'user': 5098}
      )

      generated = "\n".join([
        'var s3 = s3://a:s@bucket/video',
        'var user = 5098',
        'var vid = 1234',
        '',
        'set source = https://s3-eu-west-1.amazonaws.com/files.coconut.co/test.mp4',
        'set webhook = http://mysite.com/webhook?vid=$vid&user=$user',
        '',
        '-> mp4 = $s3/$vid.mp4'
      ])

      self.assertEqual(generated, conf)

      os.remove('coconut.conf')

    def test_submit_file(self):
      file = open('coconut.conf', 'w')
      file.write("set webhook = http://mysite.com/webhook?vid=$vid&user=$user\n-> mp4 = s3://a:s@bucket/video/$vid.mp4")
      file.close()

      job = coconut.job.create(
        conf='coconut.conf',
        source='https://s3-eu-west-1.amazonaws.com/files.coconut.co/test.mp4',
        vars={'vid': 1234, 'user': 5098}
      )

      self.assertEqual("processing", job["status"])
      self.assertTrue(job["id"] > 0)

      os.remove('coconut.conf')

    def test_set_api_key_in_job_options(self):
      job = coconut.job.create(
        api_key='k-4d204a7fd1fc67fc00e87d3c326d9b75',
        source='https://s3-eu-west-1.amazonaws.com/files.coconut.co/test.mp4'
      )

      self.assertEqual("error", job["status"])
      self.assertEqual("authentication_failed", job["error_code"])

    def test_get_job_info(self):
      conf = coconut.config.new(
        source='https://s3-eu-west-1.amazonaws.com/files.coconut.co/test.mp4',
        webhook='http://mysite.com/webhook',
        outputs={'mp4': 's3://a:s@bucket/video.mp4'}
      )

      info = coconut.job.submit(conf)
      job = coconut.job.get(info['id'])
      self.assertEqual(job['id'], info['id'])

    def test_get_all_metadata(self):
      conf = coconut.config.new(
        source='https://s3-eu-west-1.amazonaws.com/files.coconut.co/test.mp4',
        webhook='http://mysite.com/webhook',
        outputs={'mp4': 's3://a:s@bucket/video.mp4'}
      )

      job = coconut.job.submit(conf)

      time.sleep(4)
      metadata = coconut.job.get_all_metadata(job['id'])

      self.assertIsNotNone(metadata)

    def test_get_source_metadata(self):
      conf = coconut.config.new(
        source='https://s3-eu-west-1.amazonaws.com/files.coconut.co/test.mp4',
        webhook='http://mysite.com/webhook',
        outputs={'mp4': 's3://a:s@bucket/video.mp4'}
      )

      job = coconut.job.submit(conf)

      time.sleep(4)
      metadata = coconut.job.get_metadata_for(job['id'], 'source')

      self.assertIsNotNone(metadata)

    def test_set_api_version(self):
      conf = coconut.config.new(
        api_version='beta',
        source='https://s3-eu-west-1.amazonaws.com/files.coconut.co/test.mp4',
        webhook='http://mysite.com/webhook?vid=$vid&user=$user',
        outputs={
          'mp4': '$s3/vid.mp4'
        }
      )

      generated = "\n".join([
        '',
        'set api_version = beta',
        'set source = https://s3-eu-west-1.amazonaws.com/files.coconut.co/test.mp4',
        'set webhook = http://mysite.com/webhook?vid=$vid&user=$user',
        '',
        '-> mp4 = $s3/vid.mp4',
      ])

      self.assertEqual(generated, conf)

if __name__ == '__main__':
    unittest.main()