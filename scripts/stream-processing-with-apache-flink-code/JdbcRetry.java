import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.Statement;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.sink.RichSinkFunction;

public class JdbcRetry {
    private static final String URL = "jdbc:derby:memory:readings;create=true";

    public static class Store extends RichSinkFunction<Tuple2<String,Integer>> {
        private transient Connection connection;
        private transient PreparedStatement update;
        private transient PreparedStatement insert;

        @Override
        public void open(Configuration config) throws Exception {
            connection = DriverManager.getConnection(URL);
            update = connection.prepareStatement("UPDATE readings SET temp = ? WHERE sensor = ?");
            insert = connection.prepareStatement("INSERT INTO readings(temp, sensor) VALUES (?, ?)");
        }

        @Override
        public void invoke(Tuple2<String,Integer> reading, Context context) throws Exception {
            update.setInt(1, reading.f1);
            update.setString(2, reading.f0);
            if (update.executeUpdate() == 0) {
                insert.setInt(1, reading.f1);
                insert.setString(2, reading.f0);
                insert.executeUpdate();
            }
        }

        @Override
        public void close() throws Exception {
            update.close();
            insert.close();
            connection.close();
        }
    }

    public static void main(String[] args) throws Exception {
        try (Connection db = DriverManager.getConnection(URL); Statement sql = db.createStatement()) {
            sql.execute("CREATE TABLE readings(sensor VARCHAR(16) PRIMARY KEY, temp INT)");
            StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
            env.setParallelism(1);
            env.fromElements(Tuple2.of("A", 20), Tuple2.of("A", 23), Tuple2.of("A", 23))
                .addSink(new Store());
            env.execute("Repeat a JDBC write");
            try (ResultSet rows = sql.executeQuery("SELECT sensor, temp FROM readings ORDER BY sensor")) {
                while (rows.next()) {
                    System.out.println(rows.getString(1) + " " + rows.getInt(2));
                }
            }
        }
    }
}
