import cffi
import platform
from pathlib import Path

from libs.utils import get_config

# Initialize CFFI
ffi = cffi.FFI()

# Define the C interface
ffi.cdef("""
    typedef int PaHostApiIndex;
    // Forward declarations
    struct audio_buffer;

    // Type definitions
    typedef struct wave {
        unsigned int frameCount;
        unsigned int sampleRate;
        unsigned int sampleSize;
        unsigned int channels;
        void *data;
    } wave;

    typedef struct audio_stream {
        struct audio_buffer *buffer;
        unsigned int sampleRate;
        unsigned int sampleSize;
        unsigned int channels;
    } audio_stream;

    typedef struct sound {
        audio_stream stream;
        unsigned int frameCount;
    } sound;

    typedef struct music {
        audio_stream stream;
        unsigned int frameCount;
        void *ctxData;
    } music;

    // Device management
    void list_host_apis(void);
    void init_audio_device(PaHostApiIndex host_api, double sample_rate, unsigned long buffer_size);
    void close_audio_device(void);
    bool is_audio_device_ready(void);
    void set_master_volume(float volume);
    float get_master_volume(void);

    // Wave management
    wave load_wave(const char* filename);
    bool is_wave_valid(wave wave);
    void unload_wave(wave wave);

    // Sound management
    sound load_sound_from_wave(wave wave);
    sound load_sound(const char* filename);
    bool is_sound_valid(sound sound);
    void unload_sound(sound sound);
    void play_sound(sound sound);
    void pause_sound(sound sound);
    void resume_sound(sound sound);
    void stop_sound(sound sound);
    bool is_sound_playing(sound sound);
    void set_sound_volume(sound sound, float volume);
    void set_sound_pitch(sound sound, float pitch);
    void set_sound_pan(sound sound, float pan);

    // Audio stream management
    audio_stream load_audio_stream(unsigned int sample_rate, unsigned int sample_size, unsigned int channels);
    void unload_audio_stream(audio_stream stream);
    void play_audio_stream(audio_stream stream);
    void pause_audio_stream(audio_stream stream);
    void resume_audio_stream(audio_stream stream);
    bool is_audio_stream_playing(audio_stream stream);
    void stop_audio_stream(audio_stream stream);
    void set_audio_stream_volume(audio_stream stream, float volume);
    void set_audio_stream_pitch(audio_stream stream, float pitch);
    void set_audio_stream_pan(audio_stream stream, float pan);
    void update_audio_stream(audio_stream stream, const void *data, int frame_count);

    // Music management
    music load_music_stream(const char* filename);
    bool is_music_valid(music music);
    void unload_music_stream(music music);
    void play_music_stream(music music);
    void pause_music_stream(music music);
    void resume_music_stream(music music);
    void stop_music_stream(music music);
    void seek_music_stream(music music, float position);
    void update_music_stream(music music);
    bool is_music_stream_playing(music music);
    void set_music_volume(music music, float volume);
    void set_music_pitch(music music, float pitch);
    void set_music_pan(music music, float pan);
    float get_music_time_length(music music);
    float get_music_time_played(music music);

    // Memory management
    void free(void *ptr);
""")

# Load the compiled C library
# gcc -shared -fPIC -o libaudio.so audio.c -lportaudio -lsndfile -lpthread
try:
    if platform.system() == "Windows":
        lib = ffi.dlopen("libaudio.dll")
    elif platform.system() == "Darwin":
        lib = ffi.dlopen("./libaudio.dylib")
    else:  # Assume Linux/Unix
        lib = ffi.dlopen("./libaudio.so")
except OSError as e:
    print(f"Failed to load shared library: {e}")
    print("Make sure to compile your C code first.")
    if platform.system() == "Linux":
        print("Example:")
        print("gcc -shared -fPIC -o libaudio.so audio.c -lportaudio -lsndfile -lpthread")
    elif platform.system() == "Windows":
        print("On Windows, make sure you've built a DLL with MinGW or MSVC:")
        print("Example with MinGW:")
        print("gcc -shared -o libaudio.dll audio.c -lportaudio -lsndfile -lpthread")
    elif platform.system() == "Darwin":
        print("On macOS:")
        print("gcc -dynamiclib -o libaudio.dylib audio.c -lportaudio -lsndfile -lpthread")
    raise

class AudioEngine:
    def __init__(self, device_type: int, sample_rate: float, buffer_size: int, volume_presets: dict[str, float]):
        self.device_type = device_type
        if sample_rate == -1:
            sample_rate = 44100
        self.target_sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.sounds = {}
        self.music_streams = {}
        self.audio_device_ready = False
        self.volume_presets = volume_presets

        self.sounds_path = Path("Sounds")

    def list_host_apis(self):
        lib.list_host_apis() # type: ignore

    def init_audio_device(self) -> bool:
        """Initialize the audio device"""
        try:
            lib.init_audio_device(self.device_type, self.target_sample_rate, self.buffer_size) # type: ignore
            self.audio_device_ready = lib.is_audio_device_ready() # type: ignore
            file_path_str = str(self.sounds_path / 'don.wav').encode('utf-8')
            self.don = lib.load_sound(file_path_str) # type: ignore
            file_path_str = str(self.sounds_path / 'ka.wav').encode('utf-8')
            self.kat = lib.load_sound(file_path_str) # type: ignore
            if self.audio_device_ready:
                print("Audio device initialized successfully")
            return self.audio_device_ready
        except Exception as e:
            print(f"Failed to initialize audio device: {e}")
            return False

    def close_audio_device(self) -> None:
        """Close the audio device"""
        try:
            # Clean up all sounds and music
            for sound_id in list(self.sounds.keys()):
                self.unload_sound(sound_id)
            for music_id in list(self.music_streams.keys()):
                self.unload_music_stream(music_id)

            lib.unload_sound(self.don) # type: ignore
            lib.unload_sound(self.kat) # type: ignore
            lib.close_audio_device() # type: ignore
            self.audio_device_ready = False
            print("Audio device closed")
        except Exception as e:
            print(f"Error closing audio device: {e}")

    def is_audio_device_ready(self) -> bool:
        """Check if audio device is ready"""
        return lib.is_audio_device_ready() # type: ignore

    def set_master_volume(self, volume: float) -> None:
        """Set master volume (0.0 to 1.0)"""
        lib.set_master_volume(max(0.0, min(1.0, volume))) # type: ignore

    def get_master_volume(self) -> float:
        """Get master volume"""
        return lib.get_master_volume() # type: ignore

    # Sound management
    def load_sound(self, file_path: Path, name: str) -> str:
        """Load a sound file and return sound ID"""
        try:
            file_path_str = str(file_path).encode('utf-8')
            sound = lib.load_sound(file_path_str) # type: ignore

            if lib.is_sound_valid(sound): # type: ignore
                self.sounds[name] = sound
                print(f"Loaded sound from {file_path} as {name}")
                return name
            else:
                print(f"Failed to load sound: {file_path}")
                return ""
        except Exception as e:
            print(f"Error loading sound {file_path}: {e}")
            return ""

    def unload_sound(self, name: str) -> None:
        """Unload a sound by name"""
        if name in self.sounds:
            lib.unload_sound(self.sounds[name]) # type: ignore
            del self.sounds[name]
            print(f"Unloaded sound {name}")
        else:
            print(f"Sound {name} not found")

    def load_screen_sounds(self, screen_name: str) -> None:
        """Load sounds for a given screen"""
        path = self.sounds_path / screen_name
        for sound in path.iterdir():
            if sound.is_dir():
                for file in sound.iterdir():
                    self.load_sound(file, sound.stem + '_' + file.stem)
            if sound.is_file():
                self.load_sound(sound, sound.stem)

        path = self.sounds_path / 'global'
        for sound in path.iterdir():
            if sound.is_dir():
                for file in sound.iterdir():
                    self.load_sound(file, sound.stem + '_' + file.stem)
            if sound.is_file():
                self.load_sound(sound, sound.stem)

    def unload_all_sounds(self):
        """Unload all sounds"""
        for name in list(self.sounds.keys()):
            self.unload_sound(name)

    def play_sound(self, name: str, volume_preset: str) -> None:
        """Play a sound"""
        if name == 'don':
            if volume_preset:
                lib.set_sound_volume(self.don, self.volume_presets[volume_preset]) # type: ignore
            lib.play_sound(self.don) # type: ignore
        elif name == 'kat':
            if volume_preset:
                lib.set_sound_volume(self.kat, self.volume_presets[volume_preset]) # type: ignore
            lib.play_sound(self.kat) # type: ignore
        elif name in self.sounds:
            sound = self.sounds[name]
            if volume_preset:
                lib.set_sound_volume(sound, self.volume_presets[volume_preset]) # type: ignore
            lib.play_sound(sound) # type: ignore
        else:
            print(f"Sound {name} not found")

    def stop_sound(self, name: str) -> None:
        """Stop a sound"""
        if name == 'don':
            lib.stop_sound(self.don) # type: ignore
        elif name == 'kat':
            lib.stop_sound(self.kat) # type: ignore
        if name in self.sounds:
            sound = self.sounds[name]
            lib.stop_sound(sound) # type: ignore
        else:
            print(f"Sound {name} not found")

    def is_sound_playing(self, name: str) -> bool:
        if name == 'don':
            return lib.is_sound_playing(self.don) # type: ignore
        elif name == 'kat':
            return lib.is_sound_playing(self.kat) # type: ignore
        if name in self.sounds:
            sound = self.sounds[name]
            return lib.is_sound_playing(sound) # type: ignore
        else:
            print(f"Sound {name} not found")
            return False

    def set_sound_volume(self, name: str, volume: float) -> None:
        if name == 'don':
            lib.set_sound_volume(self.don, volume) # type: ignore
        elif name == 'kat':
            lib.set_sound_volume(self.kat, volume) # type: ignore
        elif name in self.sounds:
            sound = self.sounds[name]
            lib.set_sound_volume(sound, volume) # type: ignore
        else:
            print(f"Sound {name} not found")

    # Music management
    def load_music_stream(self, file_path: Path, name: str) -> str:
        """Load a music stream and return music ID"""
        file_path_str = str(file_path).encode('utf-8')
        music = lib.load_music_stream(file_path_str) # type: ignore

        if lib.is_music_valid(music): # type: ignore
            self.music_streams[name] = music
            print(f"Loaded music stream from {file_path} as {name}")
            return name
        else:
            print(f"Failed to load music: {file_path}")
            return ""

    def play_music_stream(self, name: str, volume_preset: str = '') -> None:
        """Play a music stream"""
        if name in self.music_streams:
            music = self.music_streams[name]
            lib.seek_music_stream(music, 0) # type: ignore
            if volume_preset:
                lib.set_music_volume(music, self.volume_presets[volume_preset]) # type: ignore
            lib.play_music_stream(music) # type: ignore
        else:
            print(f"Music stream {name} not found")

    def update_music_stream(self, name: str) -> None:
        """Update a music stream"""
        if name in self.music_streams:
            music = self.music_streams[name]
            lib.update_music_stream(music) # type: ignore
        else:
            print(f"Music stream {name} not found")

    def get_music_time_length(self, name: str) -> float:
        """Get the time length of a music stream"""
        if name in self.music_streams:
            music = self.music_streams[name]
            return lib.get_music_time_length(music) # type: ignore
        else:
            print(f"Music stream {name} not found")
            return 0.0

    def get_music_time_played(self, name: str) -> float:
        """Get the time played of a music stream"""
        if name in self.music_streams:
            music = self.music_streams[name]
            return lib.get_music_time_played(music) # type: ignore
        else:
            print(f"Music stream {name} not found")
            return 0.0

    def set_music_volume(self, name: str, volume: float) -> None:
        """Set the volume of a music stream"""
        if name in self.music_streams:
            music = self.music_streams[name]
            lib.set_music_volume(music, volume) # type: ignore
        else:
            print(f"Music stream {name} not found")

    def is_music_stream_playing(self, name: str) -> bool:
        """Check if a music stream is playing"""
        if name in self.music_streams:
            music = self.music_streams[name]
            return lib.is_music_stream_playing(music) # type: ignore
        else:
            print(f"Music stream {name} not found")
            return False

    def stop_music_stream(self, name: str) -> None:
        """Stop a music stream"""
        if name in self.music_streams:
            music = self.music_streams[name]
            lib.stop_music_stream(music) # type: ignore
        else:
            print(f"Music stream {name} not found")

    def unload_music_stream(self, name: str) -> None:
        """Unload a music stream"""
        if name in self.music_streams:
            music = self.music_streams[name]
            lib.unload_music_stream(music) # type: ignore
            del self.music_streams[name]
        else:
            print(f"Music stream {name} not found")

    def unload_all_music(self) -> None:
        """Unload all music streams"""
        for music_id in list(self.music_streams.keys()):
            self.unload_music_stream(music_id)

    def seek_music_stream(self, name: str, position: float) -> None:
        """Seek a music stream to a specific position"""
        if name in self.music_streams:
            music = self.music_streams[name]
            lib.seek_music_stream(music, position) # type: ignore
        else:
            print(f"Music stream {name} not found")

# Create the global audio instance
audio = AudioEngine(get_config()["audio"]["device_type"], get_config()["audio"]["sample_rate"], get_config()["audio"]["buffer_size"], get_config()["volume"])
audio.set_master_volume(0.75)
