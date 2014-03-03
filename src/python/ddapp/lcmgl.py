import ddapp.vtkAll as vtk
import ddapp.objectmodel as om
from ddapp import lcmUtils

# if bot_lcmgl cannot be important than this module will not be able to
# support lcmgl, but it can still be imported in a disabled state
try:
    import bot_lcmgl
except ImportError:
    pass


class LCMGLObject(om.ObjectModelItem):

    def __init__(self, name, actor):

        om.ObjectModelItem.__init__(self, name, om.Icons.Robot)

        self.actor = actor
        self.actor.SetUseBounds(False)
        self.addProperty('Visible', actor.GetVisibility())
        self.views = []

    def _onPropertyChanged(self, propertyName):
        om.ObjectModelItem._onPropertyChanged(self, propertyName)

        if propertyName == 'Visible':
            self.actor.SetVisibility(self.getProperty(propertyName))
            self.renderAllViews()

    def addToView(self, view):
        if view in self.views:
            return
        self.views.append(view)
        view.renderer().AddActor(self.actor)
        view.render()

    def renderAllViews(self):
        for view in self.views:
            view.render()

    def onRemoveFromObjectModel(self):
        self.removeFromAllViews()

    def removeFromAllViews(self):
        for view in list(self.views):
            self.removeFromView(view)
        assert len(self.views) == 0

    def removeFromView(self, view):
        assert view in self.views
        self.views.remove(view)
        view.renderer().RemoveActor(self.actor)
        view.render()

    def onMessage(self, msgBytes):
        self.actor.UpdateGLData(msgBytes.data())
        self.renderAllViews()


managerInstance = None

class LCMGLManager(object):

    def __init__(self, view):
        self.view = view
        self.subscriber = None
        self.enable()

    def enable(self):
        self.subscriber = lcmUtils.addSubscriber('LCMGL.*', callback=self.onMessage)

    def disable(self):
        if self.subscriber:
            lcmUtils.removeSubscriber(self.subscriber)

    def onMessage(self, msgBytes, channel):

        msg = bot_lcmgl.data_t.decode(msgBytes.data())
        drawObject = self.getDrawObject(msg.name)
        if not drawObject:
            drawObject = self.addDrawObject(msg.name, msgBytes)
        drawObject.onMessage(msgBytes)

    def getDrawObject(self, name):
        parent = om.getOrCreateContainer('LCM GL')
        return om.findChildByName(parent, name)

    def addDrawObject(self, name, msgBytes):
        actor = vtk.vtkLCMGLProp()
        obj = LCMGLObject(name, actor)
        om.addToObjectModel(obj, om.getOrCreateContainer('LCM GL'))
        obj.addToView(self.view)
        return obj


def init(view):
    if not hasattr(vtk, 'vtkLCMGLProp'):
        return None

    global managerInstance
    managerInstance = LCMGLManager(view)
    return managerInstance