#
# Copyright 2020 NVIDIA Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import PyNvCodec as nvc
import numpy as np
import sys

from threading import Thread

fout = open('log.txt', 'w')
 
class Worker(Thread):
    def __init__(self, gpuID, encFile):
        Thread.__init__(self)

        self.nvDec = nvc.PyNvDecoder(encFile, gpuID, {'rtsp_transport': 'tcp', 'max_delay': '5000000', 'bufsize': '30000k'})
        
        width, height = self.nvDec.Width(), self.nvDec.Height()
        hwidth, hheight = int(width / 2), int(height / 2)

        self.nvCvt = nvc.PySurfaceConverter(width, height, self.nvDec.Format(), nvc.PixelFormat.YUV420, gpuID)
        self.nvRes = nvc.PySurfaceResizer(hwidth, hheight, self.nvCvt.Format(), gpuID)
        self.nvDwn = nvc.PySurfaceDownloader(hwidth, hheight, self.nvRes.Format(), gpuID)
        self.num_frame = 0

    def run(self):
        try:
            while True:
                try:
                    rawSurface = self.nvDec.DecodeSingleSurface()
                    if (rawSurface.Empty()):
                        print('No more video frames', file = fout)
                        fout.flush()
                        break
                except nvc.HwResetException:
                    print('Continue after HW decoder was reset', file = fout)
                    print('Continue after HW decoder was reset')
                    fout.flush()
                    continue
 
                cvtSurface = self.nvCvt.Execute(rawSurface)
                if (cvtSurface.Empty()):
                    print('Failed to do color conversion', file = fout)
                    fout.flush()
                    break

                resSurface = self.nvRes.Execute(cvtSurface)
                if (resSurface.Empty()):
                    print('Failed to resize surface', file = fout)
                    fout.flush()
                    break
 
                rawFrame = np.ndarray(shape=(resSurface.HostSize()), dtype=np.uint8)
                success = self.nvDwn.DownloadSingleSurface(resSurface, rawFrame)
                if not (success):
                    print('Failed to download surface', file = fout)
                    fout.flush()
                    break
 
                self.num_frame += 1
                if( 0 == self.num_frame % self.nvDec.Framerate() ):
                    print(self.num_frame, file = fout)
                    fout.flush()
 
        except Exception as e:
            print(getattr(e, 'message', str(e)))
            decFile.close()
 
def create_threads(gpu_id1, input_file1):
 
    th1  = Worker(gpu_id1, input_file1)
    th2  = Worker(gpu_id1, input_file1)
    th3  = Worker(gpu_id1, input_file1)
    th4  = Worker(gpu_id1, input_file1)
    th5  = Worker(gpu_id1, input_file1)
    th6  = Worker(gpu_id1, input_file1)
    th7  = Worker(gpu_id1, input_file1)
    th8  = Worker(gpu_id1, input_file1)
 
    th1.start()
    th2.start()
    th3.start()
    th4.start()
    th5.start()
    th6.start()
    th7.start()
    th8.start()
 
    th1.join()
    th2.join()
    th3.join()
    th4.join()
    th5.join()
    th6.join()
    th7.join()
    th8.join()
 
if __name__ == "__main__":
 
    if(len(sys.argv) < 3):
        print("Provide input CLI arguments as shown above")
        exit(1)
 
    gpu_1 = int(sys.argv[1])
    input_1 = sys.argv[2]
 
    create_threads(gpu_1, input_1)
