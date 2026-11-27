import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.streaming.api.TimeCharacteristic;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.source.SourceFunction;
import org.apache.flink.streaming.api.watermark.Watermark;
import org.apache.flink.streaming.api.windowing.time.Time;

public class LateWindow {
    public static void main(String[] args) throws Exception {
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        env.setParallelism(1);
        env.setStreamTimeCharacteristic(TimeCharacteristic.EventTime);
        env.addSource(new SourceFunction<Tuple2<String, Integer>>() {
            @Override
            public void run(SourceContext<Tuple2<String, Integer>> ctx) {
                ctx.collectWithTimestamp(Tuple2.of("A", 2), 1000);
                ctx.emitWatermark(new Watermark(4999));
                ctx.collectWithTimestamp(Tuple2.of("A", 3), 3000);
                ctx.emitWatermark(new Watermark(9999));
                ctx.collectWithTimestamp(Tuple2.of("A", 7), 4000);
            }
            @Override
            public void cancel() {}
        }).keyBy(0)
          .timeWindow(Time.seconds(5))
          .allowedLateness(Time.seconds(5))
          .sum(1)
          .print();
        env.execute("Late window");
    }
}
