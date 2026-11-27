import org.apache.flink.api.common.state.ValueState;
import org.apache.flink.api.common.state.ValueStateDescriptor;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.KeyedProcessFunction;
import org.apache.flink.util.Collector;

public class TemperatureChange {
    public static class Compare extends KeyedProcessFunction<String, Tuple2<String,Integer>, String> {
        private transient ValueState<Integer> last;
        @Override
        public void open(Configuration config) {
            last = getRuntimeContext().getState(new ValueStateDescriptor<>("last", Integer.class));
        }
        @Override
        public void processElement(Tuple2<String,Integer> reading, Context ctx, Collector<String> out)
                throws Exception {
            Integer previous = last.value();
            if (previous != null && Math.abs(previous - reading.f1) > 10) {
                out.collect(reading.f0 + ": " + previous + " -> " + reading.f1);
            }
            last.update(reading.f1);
        }
    }
    public static void main(String[] args) throws Exception {
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        env.setParallelism(1);
        env.fromElements(Tuple2.of("A", 20), Tuple2.of("B", 50), Tuple2.of("A", 32))
            .keyBy(reading -> reading.f0)
            .process(new Compare())
            .print();
        env.execute("Temperature change");
    }
}
