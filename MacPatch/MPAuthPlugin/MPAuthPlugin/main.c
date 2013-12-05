//
// bannersample - simple example of GUI plugin for auth api
//

#include <Security/Authorization.h>
#include <Security/AuthorizationTags.h>
#include <Security/AuthorizationPlugin.h>

#include <stdlib.h>
#include <string.h>
#include <syslog.h>

OSStatus initializeWindow(AuthorizationMechanismRef inMechanism, int modal);
OSStatus finalizeWindow(AuthorizationMechanismRef inMechanism);
OSStatus setResult(AuthorizationMechanismRef inMechanism);

bool file_exists(const char * filename)
{
    FILE *file;
    if ((file = fopen(filename, "r")))
    {
        fclose(file);
        return true;
    }
    return false;
}

typedef struct PluginRef
{
    const AuthorizationCallbacks *callbacks;
} PluginRef;

typedef enum MechanismId
{
    kMechNone,
    kMechWindow,
	kMechModalWindow
} MechanismId;

typedef struct MechanismRef
{
    const PluginRef *plugin;
    AuthorizationEngineRef engine;
    MechanismId mechanismId;
} MechanismRef;


static OSStatus pluginDestroy(AuthorizationPluginRef inPlugin)
{
    PluginRef *plugin = (PluginRef *)inPlugin;
    free(plugin);
    return 0;
}

static OSStatus mechanismCreate(AuthorizationPluginRef inPlugin,
                                AuthorizationEngineRef inEngine,
                                AuthorizationMechanismId mechanismId,
                                AuthorizationMechanismRef *outMechanism)
{
    const PluginRef *plugin = (const PluginRef *)inPlugin;
    MechanismRef *mechanism = calloc(1, sizeof(MechanismRef));

	// Enable this to allow time to attach to SecurityAgent with gdb
    //	sleep(20);

    mechanism->plugin = plugin;
    mechanism->engine = inEngine;
    /* Check that we support the requested mechanismId. */
    if (!strcmp(mechanismId, "none"))
        mechanism->mechanismId = kMechNone;
    else if (!strcmp(mechanismId, "window"))
        mechanism->mechanismId = kMechWindow;
	else if (!strcmp(mechanismId, "modalwindow"))
        mechanism->mechanismId = kMechModalWindow;
    else
        return errAuthorizationInternal;

    *outMechanism = mechanism;

    return 0;
}
//else if (!strcmp(mechanismId, "modaltest"))
static OSStatus mechanismInvoke(AuthorizationMechanismRef inMechanism)
{
    MechanismRef *mechanism = (MechanismRef *)inMechanism;
    OSStatus status;

    switch (mechanism->mechanismId)
    {
        case kMechNone:
            break;
        case kMechWindow:
            status = initializeWindow(inMechanism,false);
            if (status)
                return status;
            // In the warning banner case, we return good immediately so that
            // the loginwindow UI will show.
            setResult(inMechanism);
            break;
        case kMechModalWindow:
            status = initializeWindow(inMechanism,true);
            if (status)
                return status;
            // Usually a UI plugin will set the result only when the user has
            // authenticated. In this sample the user "authenticates" when they
            // click the OK button
            break;
        default:
            return errAuthorizationInternal;
    }

    return noErr;
}

static OSStatus mechanismDeactivate(AuthorizationMechanismRef inMechanism)
{
    return 0;
}

static OSStatus mechanismDestroy(AuthorizationMechanismRef inMechanism)
{
    MechanismRef *mechanism = (MechanismRef *)inMechanism;
	finalizeWindow(inMechanism);
    free(mechanism);

    return 0;
}

AuthorizationPluginInterface pluginInterface =
{
    kAuthorizationPluginInterfaceVersion, //UInt32 version;
    pluginDestroy,
    mechanismCreate,
    mechanismInvoke,
    mechanismDeactivate,
    mechanismDestroy
};

OSStatus AuthorizationPluginCreate
(const AuthorizationCallbacks *callbacks, AuthorizationPluginRef *outPlugin, const AuthorizationPluginInterface **outPluginInterface)
{
    PluginRef *plugin = calloc(1, sizeof(PluginRef));

    plugin->callbacks = callbacks;
    *outPlugin = (AuthorizationPluginRef) plugin;
    *outPluginInterface = &pluginInterface;
    return 0;
}

OSStatus setResult(AuthorizationMechanismRef inMechanism)
{
    MechanismRef *mechanism = (MechanismRef *)inMechanism;
    
	if (!mechanism) {
        return errAuthorizationInternal;
    }
    return mechanism->plugin->callbacks->SetResult(mechanism->engine, kAuthorizationResultAllow);
}
