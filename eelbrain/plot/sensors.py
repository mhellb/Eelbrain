
import numpy as np
import matplotlib.pyplot as plt
try:
    from mpl_toolkits.mplot3d import Axes3D as _Axes3D
except:
    _Axes3d = None

import wx
from eelbrain.wxutils import mpl_canvas



__hide__ = ['mpl_canvas']

_ID_label_Ids = wx.NewId()
_ID_label_names = wx.NewId()
_ID_label_None = wx.NewId()


# some useful kwarg dictionaries for different plot layouts
kwargs_mono = dict(mc='k',
                   lc='.5',
                   hllc='k',
                   hlmc='k',
                   hlms=7,
                   strlc='k')


def _ax_map2d_fast(ax, sensor_net, proj='default', 
                   m='x', mew=.5, mc='b', ms=3,):
    locs = sensor_net.getLocs2d(proj=proj)
    h = plt.plot(locs[:,0], locs[:,1], m, color=mc, ms=ms, markeredgewidth=mew)
    
    return h

    
def _ax_map2d(ax, sensor_net, proj='default', 
              frame = .02,
              kwargs=dict(
                          marker='x', # symbol
                          color='b', # mpl plot kwargs ...
                          ms=3, # marker size
                          markeredgewidth=.5,
                          ls='',
                          ),
              ):
    ax.set_aspect('equal')
    ax.set_frame_on(False)
    ax.set_axis_off()
    
    _plt_map2d(ax, sensor_net, proj=proj, kwargs=kwargs)
    
    ax.set_xlim(-frame, 1+frame)
    


def _plt_map2d(ax, sensor_net, proj='default',
               kwargs=dict(
                           marker='x', # symbol
                           color='b', # mpl plot kwargs ...
                           ms=3, # marker size
                           markeredgewidth=.5,
                           ls='',
                           ),
               ):
    locs = sensor_net.getLocs2d(proj=proj)
    ax.plot(locs[:,0], locs[:,1], **kwargs)



def _plt_map2d_labels(ax, sensor_net, proj='default',
                      text='id', # 'id', 'name'
                      xpos=0, # horizontal distance from marker
                      ypos=.01, # vertical distance from marker
                      kwargs=dict( # mpl text kwargs ...
                                  color='k',
                                  fontsize=8,
                                  horizontalalignment='center', 
                                  verticalalignment='bottom',
                                  ),
                      ):
    if text == 'id':
        labels = [str(i) for i in xrange(len(sensor_net))]
    elif text == 'name':
        labels = sensor_net.names
    else:
        err = "text has to be 'id' or 'name', can't be %r" % text
        raise NotImplementedError(err)
    
    locs = sensor_net.getLocs2d(proj=proj)
    
    handles = []
    for i in xrange(len(labels)):
        x = locs[i,0] + xpos
        y = locs[i,1] + ypos
        lbl = labels[i]
        h = ax.text(x, y, lbl, **kwargs)
        handles.append(h)
    
    return handles




class map2d(mpl_canvas.CanvasFrame):
    def __init__(self, sensor_net, labels='id', proj='default',
                 figsize=(8,8), dpi=100, frame=.05, **kwargs):
        """
        **Parameters:**
        
        sensor_net : 
            sensor-net object or object containing sensor-net
        
        labels : 'id' | 'name' 
            how the sensors should be labelled
        
        proj:
            Transform to apply to 3 dimensional sensor coordinates for plotting 
            locations in a plane
        
        """
        parent = wx.GetApp().shell
        title = "Sensor Net: %s" % getattr(sensor_net, 'name', '')
        super(map2d, self).__init__(parent, title=title, 
                                    figsize=figsize, dpi=dpi)
        
        # in case sensor_net parent is submitted
        if hasattr(sensor_net, 'sensors'):
            sensor_net = sensor_net.sensors
        elif hasattr(sensor_net, 'sensor'):
            sensor_net = sensor_net.sensor
        
        # store args
        self._sensor_net = sensor_net
        self._proj = proj
        
        self.figure.set_facecolor('w')
        ax = self.figure.add_axes([frame, frame, 1 - 2 * frame, 1 - 2 * frame])
        _ax_map2d(ax, sensor_net, proj=proj, **kwargs)
        self._ax = ax
        
        self._label_h = None
        if labels:
            self.plot_labels(labels=labels)
        
        self.Show()
    
    def _init_FillToolBar(self, tb):
        tb.AddSeparator()
        
        # plot labels
        for Id, name in [(_ID_label_None, "No Labels"),
                         (_ID_label_Ids, "Ids"),
                         (_ID_label_names, "Names"),]:
            btn = wx.Button(tb, Id, name)
            tb.AddControl(btn)
            self.Bind(wx.EVT_BUTTON, self.OnPlotLabels, btn)
        
        super(map2d, self)._init_FillToolBar(tb)
    
    def OnPlotLabels(self, event):
        Id = event.GetId()
        labels = {_ID_label_None: None,
                  _ID_label_Ids: "id",
                  _ID_label_names: "name"}[Id]
        self.plot_labels(labels)
    
    def plot_labels(self, labels='id'):
        if self._label_h:
            for h in self._label_h:
                h.remove()
        
        if labels:
            h = _plt_map2d_labels(self._ax, self._sensor_net, proj=self._proj,
                                  text=labels)
        else:
            h = None
        self._label_h = h
        self.canvas.draw()




def map3d(sensor_net, marker='c*', labels=False, headBall=0):
    """not very helpful..."""
    if _Axes3D is None:
        raise ImportError("mpl_toolkits.mplot3d.Axes3D could not be imported")
    
    if hasattr(sensor_net, 'sensors'):
        sensor_net = sensor_net.sensors
    locs = sensor_net.locs3d
    fig = plt.gcf()
    ax = _Axes3D(fig)
    ax.scatter(locs[:,0], locs[:,1], locs[:,2])
    # plot head ball
    if headBall>0:
        u = np.linspace(0, 1 * np.pi, 10)
        v = np.linspace(0, np.pi, 10)
        
        x = 5 * headBall * np.outer( np.cos(u), np.sin(v))
        z = 10 * (headBall * np.outer( np.sin(u), np.sin(v)) -.5)         # vertical
        y = 5 * headBall * np.outer( np.ones(np.size(u)), np.cos(v))  # axis of the sphere
        ax.plot_surface(x, y, z,  rstride=1, cstride=1, color='w')
    #n = 100
    #for c, zl, zh in [('r', -50, -25), ('b', -30, -5)]:
    #xs, ys, zs = zip(*
    #               [(random.randrange(23, 32),
    #                 random.randrange(100),
    #                 random.randrange(zl, zh)
    #                 ) for i in range(n)])
    #ax.scatter(xs, ys, zs, c=c)
