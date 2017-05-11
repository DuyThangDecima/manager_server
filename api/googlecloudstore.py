import logging
import os

from google.appengine.api import app_identity

import cloudstorage as gcs

my_default_retry_params = gcs.RetryParams(initial_delay=0.2,
                                          max_delay=5.0,
                                          backoff_factor=2,
                                          max_retry_period=15)
gcs.set_default_retry_params(my_default_retry_params)


class CloudStorageManager():
    def __init__(self):
        pass

    def get(self):
        bucket_name = os.environ.get('BUCKET_NAME',
                                     app_identity.get_default_gcs_bucket_name())
        print bucket_name
        # self.response.headers['Content-Type'] = 'text/plain'
        # print ('Demo GCS Application running from Version: '
        #                     + os.environ['CURRENT_VERSION_ID'] + '\n')
        # print ('Using bucket name: ' + bucket_name + '\n\n')
        # [END get_default_bucket]

        bucket = '/' + bucket_name
        filename = bucket + '/demo-testfile'
        print "filename" + filename
        self.tmp_filenames_to_clean_up = []

        try:
            self.create_file(filename)
            # print ('\n\n')
            #
            # self.read_file(filename)
            # print ('\n\n')
            #
            # self.stat_file(filename)
            # print ('\n\n')
            #
            # self.create_files_for_list_bucket(bucket)
            # print ('\n\n')
            #
            # self.list_bucket(bucket)
            # print ('\n\n')
            #
            # self.list_bucket_directory_mode(bucket)
            # print ('\n\n')
        except Exception, e:
            logging.exception(e)
            self.delete_files()
            print ('\n\nThere was an error running the demo! '
                   'Please check the logs for more details.\n')
            # else:
            #     self.delete_files()
            #     print ('\n\nThe demo ran successfully!\n')

            # [START write]

    def create_file(self, filename, content):
        """
        Tao ra file Google Cloud Storage
        :param filename:
        :param content:
        :return:
        """
        logging.debug("CloudStorageManager create_file_content()");
        write_retry_params = gcs.RetryParams(backoff_factor=1.1)
        gcs_file = gcs.open(filename,
                            'w',
                            content_type='multipart/form-data',
                            options={'x-goog-meta-foo': 'foo',
                                     'x-goog-meta-bar': 'bar'},
                            retry_params=write_retry_params)
        gcs_file.write(content)
        gcs_file.close()
        return

    def read_file(self, filename):
        print "Read file"
        gcs_file = gcs.open(filename)
        content = gcs_file.read()
        gcs_file.close()
        return content
    # [END read]

    def stat_file(self, filename):
        print ('File stat:\n')

        stat = gcs.stat(filename)
        print (repr(stat))

    def create_files_for_list_bucket(self, bucket):
        print ('Creating more files for listbucket...\n')
        filenames = [bucket + n for n in ['/foo1', '/foo2', '/bar', '/bar/1',
                                          '/bar/2', '/boo/']]
        for f in filenames:
            self.create_file(f)
            # [START list_bucket]

    def list_bucket(self, bucket):
        """Create several files and paginate through them.

        Production apps should set page_size to a practical value.

        Args:
          bucket: bucket.
        """
        print ('Listbucket result:\n')

        page_size = 1
        stats = gcs.listbucket(bucket + '/foo', max_keys=page_size)
        while True:
            count = 0
            for stat in stats:
                count += 1
                print (repr(stat))
                print ('\n')

            if count != page_size or count == 0:
                break
            stats = gcs.listbucket(bucket + '/foo', max_keys=page_size,
                                   marker=stat.filename)
            # [END list_bucket]

    def list_bucket_directory_mode(self, bucket):
        print 'Listbucket directory mode result'
        for stat in gcs.listbucket(bucket + '/b', delimiter='/'):
            print stat
            if stat.is_dir:
                for subdir_file in gcs.listbucket(stat.filename, delimiter='/'):
                    print subdir_file
                    # [START delete_files]

    def delete_files(self):
        print ('Deleting files...\n')
        for filename in self.tmp_filenames_to_clean_up:
            print ('Deleting file %s\n' % filename)
            try:
                gcs.delete(filename)
            except gcs.NotFoundError:
                pass
                # [END delete_files]


                # app = webapp2.WSGIApplication([('/', MainPage)],
                #                               debug=True)
                # [END sample]

