package search;

import java.io.IOException;
import java.util.Map;
import java.util.TreeMap;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.input.FileSplit;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

/**
 * Builds the same inverted index as indexed_search in search_token.py, but
 * spread across a Hadoop cluster: for every word, how many times it appears
 * in each document.
 *
 * <p>Output lines look like: {@code guide<TAB>hitchhikers.txt=8}
 *
 * <p>Usage: {@code hadoop jar term-index-1.0.0.jar search.TermIndex <input dir> <output dir>}
 */
public class TermIndex {

  // same word rule as the Python tokenizer: letters/digits, inner apostrophes kept
  private static final Pattern WORD = Pattern.compile("[a-z0-9]+(?:'[a-z0-9]+)*");

  /** Emits ("word", "file") -> 1 for every word in a line. */
  public static class TokenMapper extends Mapper<Object, Text, Text, IntWritable> {
    private static final IntWritable ONE = new IntWritable(1);
    private final Text wordInFile = new Text();
    private String fileName;

    @Override
    protected void setup(Context context) {
      fileName = ((FileSplit) context.getInputSplit()).getPath().getName();
    }

    @Override
    public void map(Object key, Text value, Context context)
        throws IOException, InterruptedException {
      String line = value.toString().toLowerCase().replace('’', '\'');
      Matcher matcher = WORD.matcher(line);
      while (matcher.find()) {
        wordInFile.set(matcher.group() + "\t" + fileName);
        context.write(wordInFile, ONE);
      }
    }
  }

  /** Sums the counts for one ("word", "file") pair. Also used as the combiner. */
  public static class SumReducer extends Reducer<Text, IntWritable, Text, IntWritable> {
    private final IntWritable total = new IntWritable();

    @Override
    public void reduce(Text key, Iterable<IntWritable> counts, Context context)
        throws IOException, InterruptedException {
      int sum = 0;
      for (IntWritable count : counts) {
        sum += count.get();
      }
      total.set(sum);
      context.write(key, total);
    }
  }

  public static void main(String[] args) throws Exception {
    if (args.length != 2) {
      System.err.println("Usage: TermIndex <input dir> <output dir>");
      System.exit(2);
    }
    Configuration conf = new Configuration();
    // write "word<TAB>file=count" instead of "word<TAB>file<TAB>count"
    conf.set("mapreduce.output.textoutputformat.separator", "=");

    Job job = Job.getInstance(conf, "term index");
    job.setJarByClass(TermIndex.class);
    job.setMapperClass(TokenMapper.class);
    job.setCombinerClass(SumReducer.class);
    job.setReducerClass(SumReducer.class);
    job.setOutputKeyClass(Text.class);
    job.setOutputValueClass(IntWritable.class);
    FileInputFormat.addInputPath(job, new Path(args[0]));
    FileOutputFormat.setOutputPath(job, new Path(args[1]));
    System.exit(job.waitForCompletion(true) ? 0 : 1);
  }
}
