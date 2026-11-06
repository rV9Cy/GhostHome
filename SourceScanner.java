import java.nio.file.*;
import java.util.*;
import java.util.regex.*;
import java.util.stream.*;

// اجرا: java SourceScanner.java <پوشه>   (Java 17+، بدون کامپایل جدا)
public class SourceScanner {
    static final Pattern CX = Pattern.compile("\\b(if|for|while|case|catch)\\b|&&|\\|\\||\\?");
    static final Pattern TD = Pattern.compile("TODO|FIXME|HACK|XXX");
    static final Pattern SKIP = Pattern.compile("(.*/)?(\\.git|node_modules|dist|build|venv|__pycache__)/.*");
    static final Pattern EXT = Pattern.compile(".*\\.(py|js|ts|jsx|tsx|java|kt|go|rs|rb|php|c|cpp|cs)$");

    record R(String f, int loc, int cx, int td, int score) {}

    static int count(Pattern p, String t) {
        Matcher m = p.matcher(t);
        int n = 0;
        while (m.find()) n++;
        return n;
    }

    public static void main(String[] a) throws Exception {
        Path root = Paths.get(a[0]);
        List<R> rs = new ArrayList<>();
        try (Stream<Path> w = Files.walk(root)) {
            for (Path p : (Iterable<Path>) w.filter(Files::isRegularFile)::iterator) {
                String s = root.relativize(p).toString().replace('\\', '/');
                if (SKIP.matcher(s).matches() || !EXT.matcher(s).matches()) continue;
                String t;
                try { t = Files.readString(p); } catch (Exception e) { continue; }
                int loc = (int) t.lines().filter(l -> !l.isBlank()).count();
                int cx = count(CX, t), td = count(TD, t);
                rs.add(new R(s, loc, cx, td, cx + 5 * td + loc / 50));
            }
        }
        rs.sort((x, y) -> y.score() - x.score());
        StringBuilder o = new StringBuilder("[");
        for (int i = 0; i < Math.min(8, rs.size()); i++) {
            R r = rs.get(i);
            if (i > 0) o.append(',');
            o.append(String.format("{\"f\":\"%s\",\"loc\":%d,\"cx\":%d,\"todo\":%d,\"score\":%d}",
                    r.f().replace("\"", "\\\""), r.loc(), r.cx(), r.td(), r.score()));
        }
        System.out.println(o.append("]"));
    }
}
