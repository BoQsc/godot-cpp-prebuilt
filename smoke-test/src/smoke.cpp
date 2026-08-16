#include <godot_cpp/classes/node.hpp>
#include <godot_cpp/core/class_db.hpp>
#include <godot_cpp/godot.hpp>
#include <godot_cpp/variant/utility_functions.hpp>

using namespace godot;

class SmokeNode : public Node {
    GDCLASS(SmokeNode, Node)

protected:
    static void _bind_methods() {}
};

static void initialize_smoke(ModuleInitializationLevel level) {
    if (level == MODULE_INITIALIZATION_LEVEL_SCENE) {
        ClassDB::register_class<SmokeNode>();
        UtilityFunctions::print("GODOT_CPP_PREBUILT_SMOKE_OK");
    }
}

static void uninitialize_smoke(ModuleInitializationLevel level) {
    if (level == MODULE_INITIALIZATION_LEVEL_SCENE) {
        // Nothing to release.
    }
}

extern "C" {
GDExtensionBool GDE_EXPORT smoke_library_init(
        GDExtensionInterfaceGetProcAddress get_proc_address,
        const GDExtensionClassLibraryPtr library,
        GDExtensionInitialization *initialization) {
    GDExtensionBinding::InitObject init_obj(get_proc_address, library, initialization);
    init_obj.register_initializer(initialize_smoke);
    init_obj.register_terminator(uninitialize_smoke);
    init_obj.set_minimum_library_initialization_level(MODULE_INITIALIZATION_LEVEL_SCENE);
    return init_obj.init();
}
}
