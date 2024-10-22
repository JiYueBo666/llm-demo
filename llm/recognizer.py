import sys
import sherpa_onnx
import sounddevice as sd
from utils import get_green_logger, time_logger

logger = get_green_logger()


class Recognizer:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Recognizer, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, callback=None, endpoint_callback=None):
        if not self._initialized:
            self._initialized = True
            self.tokens = "./zipformer/tokens.txt"
            self.encoder = "./zipformer/encoder-epoch-99-avg-1.onnx"
            self.decoder = "./zipformer/decoder-epoch-99-avg-1.onnx"
            self.joiner = "./zipformer/joiner-epoch-99-avg-1.onnx"
            self.callback = callback
            self.endpoint_callback = endpoint_callback
            self.create_recognizer()

    @classmethod
    def get_instance(cls, callback=None, endpoint_callback=None):
        if cls._instance is None:
            cls._instance = cls(callback, endpoint_callback)
        return cls._instance

    @time_logger
    def create_recognizer(self):
        logger.info("Creating recognizer.....")
        self.online_recognizer = sherpa_onnx.OnlineRecognizer.from_transducer(
            tokens=self.tokens,
            encoder=self.encoder,
            decoder=self.decoder,
            joiner=self.joiner,
            num_threads=1,
            sample_rate=16000,
            feature_dim=80,
            enable_endpoint_detection=True,
            rule1_min_trailing_silence=2.4,
            rule2_min_trailing_silence=1.2,
            rule3_min_utterance_length=300,  # it essentially disables this rule
            decoding_method="greedy_search",
            provider="cpu",
            hotwords_file="",
            hotwords_score=1.5,
            blank_penalty=0.0,
        )
        logger.info("Recognizer created successfully")

    def online_recognize(self):
        devices = sd.query_devices()
        if len(devices) == 0:
            logger.error("No microphone devices found")
            sys.exit(0)
        logger.info(f"Using device: {devices[0]['name']}")
        sample_rate = 48000
        samples_per_read = int(0.1 * sample_rate)
        # 创建识别流
        stream = self.online_recognizer.create_stream()
        last_result = ""
        segment_id = 0
        logger.info("Start recording...")
        with sd.InputStream(channels=1, dtype="float32", samplerate=sample_rate) as s:
            while True:
                samples, _ = s.read(samples_per_read)  # a blocking read
                samples = samples.reshape(-1)
                stream.accept_waveform(sample_rate, samples)
                while self.online_recognizer.is_ready(stream):
                    self.online_recognizer.decode_stream(stream)

                is_endpoint = self.online_recognizer.is_endpoint(stream)
                result = self.online_recognizer.get_result(stream)
                if result and (last_result != result):
                    last_result = result
                    logger.info(f"Segment {segment_id}: {result}")
                    if self.callback:
                        self.callback(result)
                if is_endpoint and result:
                    logger.info(f"Endpoint detected. Segment {segment_id}: {result}")
                    if self.endpoint_callback:
                        self.endpoint_callback()
                    segment_id += 1
                    self.online_recognizer.reset(stream)
                    last_result = ""  # 重置 last_result
