#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
#  
#  FIRSTCTRL - Pupil remapping control software
#  Copyright (C) 2016  Guillaume Schworer
#  
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#  
#  For any information, bug report, idea, donation, hug, beer, please contact
#    guillaume.schworer@gmail.com
#
###############################################################################

import time
import datetime
from threading import Thread
from astropy.io import fits
from pyMilk.interfacing.isio_shmlib import SHM

# from FIRST_mems.com_zmq import PColors
from com_zmq import PColors

from tqdm import tqdm
import matplotlib.pyplot as plt
# import scipy.optimize
# from scipy import optimize
# from scipy.optimize import curve_fit


# from FIRST_mems import core
import core
os = core.os
np = core.np
glob = core.glob
IrisAO_API = core.IrisAO_API

plt.ion()

################################################################################
##################             Global variables             ####################
################################################################################


CURRENT_PATH        = "Documents/lib/firstctrl/FIRST_mems/firstv1_mems/"
MEMS_INDEX_NAME     = "mems_index.fits"
MEMS_OPD_NAME       = "mems_opd.fits"
MEMS_CENTERS_NAME   = "mems_centers.txt"
FIRST_SEGMENTS      = [15, 19, 16, 29, 17, 20, 33, 24, 37]

################################################################################
##################         MemsCtrl class defintion         ####################
################################################################################


__all__ = ['MemsCtrl']


class MemsCtrl(Thread):
    def __init__(self, publisher, milk_gui):
        super().__init__()

        self.pub = publisher
        self.running = True
        self.milk_solution = milk_gui

        # Define the attributes
        self._INITIALDIR = os.getcwd()
        self._connected = False
        self._pos = 0*np.ones((core.NSEGMENTS, 3))
        self._off = np.c_[np.ones((core.NSEGMENTS, 2))*core.TIPTILTMIN,
                          0*np.ones((core.NSEGMENTS, 1))]
        self._on = 0*np.ones((core.NSEGMENTS, 3))

        if self.milk_solution:
            # Prepare the maps to be ploted
            self._init_maps()

            # Prepare the shared memory
            self.data_plot = SHM('irisaoim', ((self.map_width, self.map_height), np.float64), location=-1, shared=1)

            # Start the mems
            self.start()
        else:
            self.connect()
            self.flat()

    def __enter__(self):
        #
        return self

    def __del__(self):
        self.flat()
        self.disconnect()

    __exit__ = __del__

    def _pprint(self, message):
        '''
        Print message with a color define in the class PColors.
        '''
        self.pub.pprint(PColors.MEMS + str(message) + PColors.ENDC)

    def start(self):
        # Start the mems
        self.connect()
        self.flat()

        # Start the py-milk live feed
        os.system("shmImshow.py irisaoim &")

        # Push the initial opd map
        self._init_figure()

        # Start the Thread
        super().start()

    def stop(self):
        self._pprint("    Closing mems...\n")
        time.sleep(1)
        self.running = False
        time.sleep(1)
        self.join()

    def connect(self):
        """
        Connects to the Mems
        """
        # already connected
        if self._connected:
            return 0
        # hack to CD to the folder with the cal files
        os.chdir(core.PATHCALMEMS)
        disableHardware = False
        self._mirror = IrisAO_API.MirrorConnect(core.MIRRORNUM,
                                                core.DRIVERNUM,
                                                disableHardware)
        # CD to previous folder
        os.chdir(self._INITIALDIR)
        self._connected = True

    def disconnect(self):
        """
        Disconnects the Mems
        """
        if not self._connected:
            self._pprint("ERROR: Not connected to Mems")
            return 0
        self.flat()
        IrisAO_API.MirrorRelease(self._mirror)
        self._connected = False

    def exit(self):
        """
        Disconnects the Mems
        """
        self.disconnect()

    @property
    def connected(self):
        """
        If there is an active link to the Mems
        """
        return self._connected

    @connected.setter
    def connected(self, value):
        self._pprint("Read-only")

    @property
    def first_nseg(self):
        return len(core.FIRSTSEGS)

    @first_nseg.setter
    def first_nseg(self, value):
        self._pprint('Read-only')

    @property
    def first_seg(self):
        """
        The favorite segments of First
        """
        return core.FIRSTSEGS

    @first_seg.setter
    def first_seg(self, value):
        self._pprint('Read-only')
        
    def flat(self):
        """
        Sets all tip, tilt, piston to nil
        """
        if not self._connected:
            self._pprint("ERROR: Not connected to Mems")
            return 0
        IrisAO_API.MirrorCommand(self._mirror,
                                 IrisAO_API.MirrorInitSettings)
        self._pos = np.zeros((core.NSEGMENTS, 3))

    def _moveit(self, arr, elm):
        elm, sz = self._clean_segment(elm)
        if elm is None:
            self._pprint("Wrong input, should be int, list of int, 'first', or 'all'")
            return 0
        piston, tip, tilt = arr[:, :][core.mask_elm(elm)].T
        self.set_pos(elm=elm, piston=piston, tip=tip, tilt=tilt)

    def off(self, elm='all'):
        """
        Sets all piston to nil; sets tip & tilt to min range
        """
        self._moveit(self._off, elm)

    def on(self, elm='first'):
        """
        Sets all piston to nil; sets tip & tilt to min range
        """
        self._moveit(self._on, elm)

    def _clean_segment(self, elm):
        if isinstance(elm, int):
            return [elm], 1
        elif isinstance(elm, str):
            if elm.lower() == 'first':
                elm = core.FIRSTSEGS
            elif elm.lower() == 'all':
                elm = [i for i in range(1, core.NSEGMENTS + 1)]
        elif hasattr(elm, '__iter__'):
            elm = [item for item in core.clean_list(elm) if 0 < item <= core.NSEGMENTS]
        else:
            return None, None
        return elm, len(elm)

    def get_pos(self, elm):
        """
        Gets the positions of the mems segments

        ex: tip, tilt, piston = m.get_pos('first')

        Input argument elm can be:
          * int -> 1 segment
          * list of int -> n segment
          * 'first' -> the first segments
          * 'all' -> all segments
        """
        if not self._connected:
            self._pprint("ERROR: Not connected to Mems")
            return 0
        elm, sz = self._clean_segment(elm)
        if elm is None:
            self._pprint("Wrong input, should be int, list of int, 'first', or 'all'")
            return 0
        # (tip, tilt, piston), locked, reachable
        return np.asarray(IrisAO_API.\
                  GetMirrorPosition(self._mirror, elm)[0]).T

    def set_pos(self, elm, piston=None, tip=None, tilt=None):
        """
        Sets the positions of the mems segments

        Input argument elm can be:
          * int -> 1 segment
          * list of int -> n segment
          * 'first' -> the first segments
          * 'all' -> all segments

        tip, tilt, piston can be left to None to remain unchanged
        if not None, tip, tilt and piston should be a list of floats
        with same size as elm
        """
        if not self._connected:
            self._pprint("ERROR: Not connected to Mems")
            return
        elm, sz = self._clean_segment(elm)
        # check input

        if piston is None:
            piston = self._pos[:, 0][core.mask_elm(elm)]
        elif np.size(piston) != sz:
            self._pprint('Wrong size, should be same as elm: {}'.format(sz))
            return
        piston = core.clean_pos(piston, ax='piston')

        if tip is None:
            tip = self._pos[:, 1][core.mask_elm(elm)]
        elif np.size(tip) != sz:
            self._pprint('Wrong size, should be same as elm: {}'.format(sz))
            return
        tip = core.clean_pos(tip, ax='tiptilt')
        
        if tilt is None:
            tilt = self._pos[:, 2][core.mask_elm(elm)]
        elif np.size(tilt) != sz:
            self._pprint('Wrong size, should be same as elm: {}'.format(sz))
            return
        tilt = core.clean_pos(tilt, ax='tiptilt')
        
        new_val = np.vstack((piston, tip, tilt)).T
        self._pos[core.mask_elm(elm), :] = new_val
        new_val = [tuple(item) for item in new_val]
        # print(new_val)
        # replace in local values
        IrisAO_API.SetMirrorPosition(self._mirror, elm, new_val)
        IrisAO_API.MirrorCommand(self._mirror, IrisAO_API.MirrorSendSettings)

    def _shape_save(self, name, arr, override):
        if not self._connected:
            self._pprint("ERROR: Not connected to Mems")
            return
        if os.path.isfile(name) and not bool(override):
            self._pprint("File '{}' already exists".format(name))
            return
        np.savetxt(name, arr, header="PISTON, TIP, TILT")
        self._pprint("Saved in '{}'".format(name))

    def shape_save(self, name, override=False):
        """
        Saves the current shape into a file

        Args:
          * name (str): the name of the file
          * override (bool): whether to override a file if already
            existing
        """
        name = core.make_filepath(name, core.SHAPEFILENAME)
        self._pos = self.get_pos('all').T
        self._shape_save(name, self._pos, override)

    def shape_on_save(self, name, override=False):
        """
        Saves the current shape ON into a file

        Args:
          * name (str): the name of the file
          * override (bool): whether to override a file if already
            existing
        """
        name = core.make_filepath(name, core.SHAPEONFILENAME)
        self._shape_save(name, self._pos, override)
        self._on = self._pos.copy()

    def shape_off_save(self, name, override=False):
        """
        Saves the current shape OFF into a file

        Args:
          * name (str): the name of the file
          * override (bool): whether to override a file if already
            existing
        """
        name = core.make_filepath(name, core.SHAPEOFFFILENAME)
        self._shape_save(name, self._pos, override)
        self._off = self._pos.copy()

    def shape_list(self):
        """
        Shows all available shape files saved
        """
        self._pprint("\n".join(core.list_filepath(core.SHAPEFILENAME)))

    def shape_on_list(self):
        """
        Shows all available shape ON files saved
        """
        self._pprint("\n".join(core.list_filepath(core.SHAPEONFILENAME)))

    def shape_off_list(self):
        """
        Shows all available shape OFF files saved
        """
        self._pprint("\n".join(core.list_filepath(core.SHAPEOFFFILENAME)))

    def _shape_delete(self, name):
        if os.path.isfile(name):
            os.remove(name)
            self._pprint("Removed: '{}'".format(name))
        else:
            self._pprint("File '{}' not found".format(name))

    def shape_delete(self, name):
        """
        Deletes a shape file saved

        Args:
          * name (str): the name of the file
        """
        self._shape_delete(
            core.make_filepath_nostamp(name, core.SHAPEFILENAME))

    def shape_on_delete(self, name):
        """
        Deletes a shape ON file saved

        Args:
          * name (str): the name of the file
        """
        self._shape_delete(
            core.make_filepath_nostamp(name, core.SHAPEONFILENAME))

    def shape_off_delete(self, name):
        """
        Deletes a shape OFF file saved

        Args:
          * name (str): the name of the file
        """
        self._shape_delete(
            core.make_filepath_nostamp(name, core.SHAPEOFFFILENAME))

    def _shape_load(self, name):
        if not self._connected:
            self._pprint("ERROR: Not connected to Mems")
            return None
        if os.path.isfile(name):
            l = np.loadtxt(name)
            self._pprint("Loaded '{}'".format(name))
            return l
        else:
            self._pprint("File '{}' not found".format(name))
            return None

    def shape_load(self, name_file):
        """
        Loads a shape file previously saved

        Args:
          * name (str): the name of the file
        """
        # name = core.make_filepath_nostamp(name, core.SHAPEFILENAME)
        # res = self._shape_load(name)
        # if res is not None:
        #     self._moveit(np.loadtxt(name), 'all')
        name = '/home/first/Documents/lib/firstctrl/data/optim_commands/'+name_file
        self.command_loaded = np.load(name)
        self.set_pos('all', tip=self.command_loaded[0,:], tilt = self.command_loaded[1,:])

    def shape_on_load(self, name):
        """
        Loads a shape ON file previously saved

        Args:
          * name (str): the name of the file
        """
        name = core.make_filepath_nostamp(name, core.SHAPEONFILENAME)
        res = self._shape_load(name)
        if res is not None:
            self._on = np.loadtxt(name)

    def shape_off_load(self, name):
        """
        Loads a shape OFF file previously saved

        Args:
          * name (str): the name of the file
        """
        name = core.make_filepath_nostamp(name, core.SHAPEOFFFILENAME)
        res = self._shape_load(name)
        if res is not None:
            self._off = np.loadtxt(name)

    ##### Seb & Nick's additions - Might be broke #########
    def piston_scan(self, elm, piston_begin, piston_end, step, wait_time):
        """
        Piston Scan function. Format is piston_scan(Seg#, Where to begin, Where to end, stepsize,wait time).
        It will then scan through once. 
        """
        nb_steps=int((abs(piston_end)+abs(piston_begin))/step)
        # print(nb_steps)
        # print('Initiating ramp from '+str(piston_begin)+' to '+str(piston_end)+' with '+str(nb_steps)+' steps')
        self._pprint("MEMS Scanning....")
        for i in range(0, nb_steps+1):
            self.set_pos(elm, piston_begin+i*step, 0, 0)
            # print(piston_begin+i*step)
            # print('Piston step nb '+str(i+1))
            time.sleep(wait_time)

    # Gui methods
    def run(self):
        if self.milk_solution:
            while self.running:
                if self.connected:
                    # Get pos of mems
                    piston, tip, tilt = self.get_pos('all')

                    # Compute the new opd map
                    self._update_map(piston, tip, tilt)

                    # Push data to the sahred memory
                    self.data_plot.set_data(self.map_opd.astype(np.float32))
                else:
                    self._init_figure()

    def _compute_radii(self):
        for pix_x in range(self.map_height):
            for pix_y in range(self.map_width):
                seg_ind = self.map_index[pix_x, pix_y]
                if seg_ind != 0:
                    radius_x = pix_x - self.map_centers[0, seg_ind - 1]
                    self.map_radius_x[pix_x, pix_y] = radius_x
                    radius_y = pix_y - self.map_centers[1, seg_ind - 1]
                    self.map_radius_y[pix_x, pix_y] = radius_y

    def _init_maps(self):
        self.map_index, self.map_index_h = fits.getdata(CURRENT_PATH + MEMS_INDEX_NAME, header=True)
        self.map_height, self.map_width = np.shape(self.map_index)
        self.map_opd = np.ones((self.map_height, self.map_width))
        self.map_opd[self.map_index == 0] = 0
        self.map_centers = np.loadtxt(CURRENT_PATH + MEMS_CENTERS_NAME, dtype=np.int)
        self.map_radius_x = np.ones((self.map_height, self.map_width))
        self.map_radius_y = np.ones((self.map_height, self.map_width))
        self._compute_radii()

    def _init_figure(self):
        #
        self.data_plot.set_data(self.map_opd.astype(np.float32))

    def _update_map(self, piston_arr, tip_arr, tilt_ar):
        """Compute piston, tip and tilt in opd unit."""
        for seg_ind in range(37):
            tip_value = self.map_radius_x[self.map_index == seg_ind + 1] * np.sin(tip_arr[seg_ind] * 10 ** (-3))
            tilt_value = self.map_radius_y[self.map_index == seg_ind + 1] * np.sin(tilt_ar[seg_ind] * 10 ** (-3))
            self.map_opd[self.map_index == seg_ind + 1] = piston_arr[seg_ind] + tip_value + tilt_value

    #################################################################################
    # Optimization procedure
    #################################################################################

    def flat_field_command(self,seg):
        for s in range(9):
            optim_command = self.command_loaded
            if FIRST_SEGMENTS[s] != seg :
                optim_command[:,FIRST_SEGMENTS[s]] = 2.



    #################################################################################
    # Optimization procedure
    #################################################################################

    def optimization(self, window_scan=4, step_scan=0.1, n_raw=1, Target='Name_of_Target'):######################

        self.flux=SHM("first_photom_flux_val",verbose=False)


        def spiral(a):##############################################################################################
                sp = np.zeros((a**2,2))
                switch = np.zeros(a**2)
                x = y = 0
                dx = 0
                dy = -1
                for i in range(a**2):
                    sp[i,:] = np.array([x,y], dtype=float)/a*2
                    if x == y or (x < 0 and x == -y) or (x > 0 and x == 1-y):
                        switch[i] = True
                        dx, dy = -dy, dx
                    else:
                        switch[i] = False
                    x, y = x+dx, y+dy
                return sp,switch

        def show_optim(res_opt,Target):######################################################################################
            plt.figure()
            # plt.subplot(4,3,1)
            idplt=1
            cmin=np.min(self.res_optim)
            cmax=np.max(self.res_optim)
            for id in range(9):
                plt.subplot(3,3,idplt)
                plt.imshow(self.res_optim[:,:,id],origin='lower')
                plt.ylabel('#'+str(FIRST_SEGMENTS[id]))
                idplt+=1
                #plt.clim([cmin,cmax])

            
            self.date=datetime.datetime.today().strftime('%Y-%m-%d')
            self.clock=datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            path_save='/home/first/Documents/lib/firstctrl/data/Optim_maps/'+self.date+'/'+self.clock+'_'+Target+'/'
            if not os.path.exists(path_save):
                os.makedirs(path_save)
            plt.savefig(path_save+'optim_result.png',orientation='landscape')
            # for i in range(8):
            #     plt.imsave(path_save+'optim_'+self.clock+'_'+str(i+1)+'.pdf', self.res_optim[:,:,i])
            #     hdu=fits.PrimaryHDU(self.res_optim[:,:,i])
            #     hdu.writeto(path_save+'optim_'+self.clock+'_'+str(i+1)+'.fits')

        def process_optim_map(data, Target, window_scan, step_scan, seg_id):######################################################################################

            def gaussian(height, center_x, center_y, width_x, width_y):
                """Returns a gaussian function with the given parameters"""
                width_x = float(width_x)
                width_y = float(width_y)
                return lambda x,y: height*np.exp(
                    -(((center_x-x)/width_x)**2+((center_y-y)/width_y)**2)/2)
                
            def moments(data):
                """Returns (height, x, y, width_x, width_y)
                the gaussian parameters of a 2D distribution by calculating its
                moments """
                total = data.sum()
                X, Y = np.indices(data.shape)
                x = (X*data).sum()/total
                y = (Y*data).sum()/total
                col = data[:, int(y)]
                width_x = np.sqrt(np.abs((np.arange(col.size)-y)**2*col).sum()/col.sum())
                row = data[int(x), :]
                width_y = np.sqrt(np.abs((np.arange(row.size)-x)**2*row).sum()/row.sum())
                height = data.max()
                return height, x, y, width_x, width_y

            def fitgaussian(data):
                """Returns (height, x, y, width_x, width_y)
                the gaussian parameters of a 2D distribution found by a fit"""
                params = moments(data)
                errorfunction = lambda p: np.ravel(gaussian(*p)(*np.indices(data.shape)) -
                                                   data)
                p, success = scipy.optimize.leastsq(errorfunction, params)
                return p
                

        
            image=data
            plt.figure()
            plt.imshow(image,origin='lower')
            params=fitgaussian(image)
            fit=gaussian(*params)
            
            plt.contour(fit(*np.indices(image.shape)), cmap=plt.cm.copper)
            ax=plt.gca()
            (height,x,y,width_x,width_y)=params
            
            #print('(%.1f,%.1f)'%(x,y))
            plt.gca().set_title('Optimization map - '+Target+' - Scan='+str(window_scan)+'mas Step='+str(step_scan)+'mas')
            plt.text(0.95,0.05,"""
            Center:(%.1f,%.1f)
            Width_x:%.1f
            Width_y:%.1f"""%(x,y,width_x,width_y),fontsize=10,horizontalalignment='right',verticalalignment='bottom',transform=ax.transAxes,color='w')
            
            path_save='/home/first/Documents/lib/firstctrl/data/Optim_maps/'+self.date+'/'+self.clock+'_'+Target+'/'
            plt.savefig(path_save+Target+'_processed_Seg'+str(seg_id)+'.png')

            return x,y


        #############################
        #         Init scan         #
        #############################

        npt                 = int(window_scan/step_scan) 
        self._pprint('Npt:'+str(npt))
        sp, switch          = spiral(npt)
        sp                  = sp*(window_scan/2.)

        
        tip0,tilt0          = 0,0
        self.res_optim_raw  = np.zeros((npt, npt, n_raw, 9))
        self.res_optim      = np.zeros((npt, npt, 9))
        indtip0             = npt/2.
        indtilt0            = npt/2.

        self.map_tip        = np.zeros((npt,npt))
        self.map_tilt       = np.zeros((npt,npt))

        indtip_opt          = np.zeros(9)
        indtilt_opt         = np.zeros(9)

        tip_command         = np.zeros(37)
        tilt_command        = np.zeros(37)
        

    
        #############################
        #      First position       #
        #############################
        for s in range(9):
            #self._pprint('Test1')
            tip_command[FIRST_SEGMENTS[s]-1] = tip0
            tilt_command[FIRST_SEGMENTS[s]-1] = tilt0
        #self._pprint('Test2')
        self.set_pos('all', tip = tip_command, tilt = tilt_command)
        #time.sleep(1.)
        #self._pprint('Test3')
        
        self.map_tip [np.int(np.ceil(indtip0-1)),np.int(np.ceil(indtilt0-1))] = tip0
        self.map_tilt[np.int(np.ceil(indtip0-1)),np.int(np.ceil(indtilt0-1))] = tilt0

        for r in range(n_raw):
            #self._pprint('Test4')
            #self._pprint(self.flux.get_data(True, True, timeout = 1.))
            #self._pprint(self.res_optim_raw[np.int(np.ceil(indtip0-1)),np.int(np.ceil(indtilt0-1)),r,:])
            self.res_optim_raw[np.int(np.ceil(indtip0-1)),np.int(np.ceil(indtilt0-1)),r,:]   = self.flux.get_data(True, True, timeout = 1.)
            time.sleep(0.06)
            
           
        self.res_optim[np.int(np.ceil(indtip0-1)),np.int(np.ceil(indtilt0-1)),:] = np.mean(self.res_optim_raw[np.int(np.ceil(indtip0-1)),np.int(np.ceil(indtilt0-1)),:,:],axis=0)
        #print(self.res_optim[int(indphi0)-1,int(indtheta0)-1])
        #print('Index: x:',np.ceil(indphi0-1),'y:',np.ceil(indtheta0-1))
        #############################
        #  Start spiral movement    #
        #############################
        for i in tqdm(range(1,npt**2)):
        # for i in range(1,npt**2):

            xi                                        = tip0+sp[i,0]
            yi                                        = tilt0+sp[i,1]
            for s in range(9):
                tip_command[FIRST_SEGMENTS[s]-1] = xi
                tilt_command[FIRST_SEGMENTS[s]-1] = yi

            # self._pprint('Position: x:')
            # self._pprint(xi)
            # self._pprint('Position y:')
            # self._pprint(yi)

            indtip                                    = indtip0+sp[i,0]*(npt)/4.
            indtilt                                   = indtilt0+sp[i,1]*(npt)/4.

            # self._pprint('Ind Tip:'+str(indtip))
            # self._pprint('Ind Tilt:'+str(indtilt))

            self.map_tip [np.int(np.ceil(indtip-1)),np.int(np.ceil(indtilt-1))] = xi
            self.map_tilt[np.int(np.ceil(indtip-1)),np.int(np.ceil(indtilt-1))] = yi
            #self._pprint('Index: x:',np.ceil(indphi-1),'y:',np.ceil(indtheta-1))
            if i==1:
                axis = "x"
                self.set_pos('all', tip = tip_command)
                #self._pprint(i, axis, xi-tip0, yi-tilt0)
            if i > 1:
                if switch[i-1]:
                    if axis == "y":
                        #con.open(self.conex_id_phi)
                        axis = "x"
                    else:
                        #con.open(self.conex_id_theta)
                        axis = "y"
                if axis == "x":
                    self.set_pos('all', tip = tip_command)
                else:
                    self.set_pos('all', tilt = tilt_command)

            
            time.sleep(0.001)
            #############################
            #     Take Flux values      #
            #############################   
            for r in range(n_raw):
                self.res_optim_raw[np.int(np.ceil(indtip-1)),np.int(np.ceil(indtilt-1)),r,:]  = self.flux.get_data(True, True, timeout = 1.)
                time.sleep(0.06)
            
           
            self.res_optim[np.int(np.ceil(indtip-1)),np.int(np.ceil(indtilt-1)),:]            = np.mean(self.res_optim_raw[np.int(np.ceil(indtip-1)),np.int(np.ceil(indtilt-1)),:,:],axis=0)
            #print(self.res_optim[int(indphi)-1,int(indtheta)-1])
            
        #############################
        #  Show/save Optimization   #
        #############################
        show_optim(self.res_optim,Target)


        # #############################
        # #    Extract optimal pos    #
        # #############################
        # for s in range(9):
        #     indtip_opt[s], indtilt_opt[s]  = process_optim_map(self.res_optim[:,:,s], Target, window_scan, np.around(step_scan,decimals=2), FIRST_SEGMENTS[s])
        # tip_opt   = tip0  -(indtip0 -indtip_opt )*step_scan
        # tilt_opt  = tilt0 -(indtilt0-indtilt_opt)*step_scan
        # self._pprint('Optimal process position in tip:')
        # self._pprint(tip_opt)
        # self._pprint('Optimal process position in tilt:')
        # self._pprint(tilt_opt)

        for s in range(9):
            indtip_opt[s], indtilt_opt[s]  = np.unravel_index(self.res_optim[:,:,s].argmax(),(npt,npt))
        tip_opt   = tip0  -(indtip0 -indtip_opt )*step_scan
        tilt_opt  = tilt0 -(indtilt0-indtilt_opt)*step_scan
        self._pprint('Optimal process position in tip:')
        self._pprint(tip_opt)
        self._pprint('Optimal process position in tilt:')
        self._pprint(tilt_opt)

        for s in range(9):
            tip_command[FIRST_SEGMENTS[s]-1] = tip_opt[s]
            tilt_command[FIRST_SEGMENTS[s]-1] = tilt_opt[s]

        #############################
        #    Move to optimal pos    #
        #############################
        self.set_pos('all', piston = np.zeros(37)+0.01, tip=tip_command, tilt = tilt_command)


        #############################
        #      Save info optim      #
        #############################
        optim_command = [tip_command, tilt_command]
        path_save_commands = '/home/first/Documents/lib/firstctrl/data/optim_commands/'
        if not os.path.exists(path_save_commands):
            os.makedirs(path_save_commands)
        np.save(path_save_commands+self.clock+'_Target.npy', optim_command)



        # # if phi_opt < np.around(np.min(self.map_phi),decimals=4) or phi_opt > np.around(np.max(self.map_phi),decimals=4):
        # #     indphi_opt, indtheta_opt = np.unravel_index(self.res_optim[:,:,ird_channel_opt].argmax(),(npt,npt))
        # #   phi_opt = self.map_phi[indphi_opt, indtheta_opt]
        # #   print('Warning : Phi optimal value out of the box')

        # # if theta_opt < np.around(np.min(self.map_theta),decimals=4) or theta_opt > np.around(np.max(self.map_theta),decimals=4):
        # #     indphi_opt, indtheta_opt = np.unravel_index(self.res_optim[:,:,ird_channel_opt].argmax(),(npt,npt))
        # #     theta_opt = self.map_theta[indphi_opt, indtheta_opt]
        # #     print('Warning : Theta optimal value out of the box')

        # #scan_mas=(((np.max(self.map_phi)-np.min(self.map_phi))*1e3)/10.)*53
        # #step_scan=(((self.map_phi[1,0]-self.map_phi[0,0])*1e3)/10.)*53
        # scan_mas = 1
        # step_scan = 1
        # print('Scan in x from ',np.around(np.min(self.map_phi),decimals=4),'to',np.around(np.max(self.map_phi),decimals=4), '--', np.around(scan_mas,decimals=0),'mas')
        # print('Scan in y from ',np.around(np.min(self.map_theta),decimals=4),'to',np.around(np.max(self.map_theta),decimals=4))
        # print('Step:',np.around((self.map_phi[1,0]-self.map_phi[0,0])*1e3,decimals=1),'um', '--', np.around(step_scan,decimals=0),'mas' )
        
        # print('Optimal position in phi:',np.around(phi_opt, decimals = 6), 'in theta:',np.around(theta_opt, decimals=6))
        
      

        # # con.open(self.conex_id_phi)
        # # con.move(xpos, "", False)
        # # con.close()
        # # con.open(self.conex_id_theta)
        # # con.move(ypos, "", False)
        # # con.close()


        # # #############################
        # # #      Save info optim      #
        # # #############################
        # # info={'Target'                : Target,
        # #       'x init'                : phi0,
        # #       'y init'                : theta0,
        # #       'Windows size (mas)'    : window_scan,
        # #       'Step size (mas)'       : step_scan,
        # #       'Number frames'         : n_raw,
        # #       'x optimal'             : xpos,
        # #       'y optimal'             : ypos,
        # #       }
        
        # # #date=datetime.datetime.today().strftime('%Y-%m-%d')
        # # #clock=datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        # # self.save_info(info, '/home/scexao/Documents/sebviev/ird_pcfi/data/Optim_maps/'+self.date+'/'+self.clock+'_'+Target+'/info_'+self.clock+'_'+Target+'.txt')
        
