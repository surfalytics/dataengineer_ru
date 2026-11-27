import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;

public class SensorTotals {
    public static void main(String[] args) throws Exception {
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        env.setParallelism(1);
        env.fromElements(Tuple2.of("A", 2), Tuple2.of("B", 5), Tuple2.of("A", 3))
            .keyBy(0)
            .sum(1)
            .print();
        env.execute("Sensor totals");
    }
}
