import java.io.File;
import java.io.IOException;
import java.util.Set;
//import java.util.StringTokenizer;

import org.apache.commons.io.FileUtils;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.MapWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.io.Writable;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

public class Stripes{

  public static class StripesOccurrenceMapper
       extends Mapper<Object, Text, Text, MyMapWriter>{
	  private MyMapWriter map = new MyMapWriter();
	  //private final static IntWritable one = new IntWritable(1);
	  private Text word = new Text();

    public void map(Object key, Text value, Context context
                    ) throws IOException, InterruptedException {
      String[] values = value.toString().split(" ");
      for(int i=0; i < values.length;i++){
    	  word.set(values[i]);
    	  map.clear();
    	  for(int j=0; j<values.length;j++){
    		  if(!values[i].trim().equals("") && !values[j].trim().equals("")){
    		  if(j==i) continue;
    		  Text text = new Text(values[j]);
    		  if(map.containsKey(text)){
                  IntWritable count = (IntWritable)map.get(text);
                  count.set(count.get()+1);
               }else{
                  map.put(text,new IntWritable(1));
               }
    		  }
    	  }
    	  context.write(word, map);
      }
      
    }
  }

  public static class StripReducer
       extends Reducer<Text,MyMapWriter,Text,MyMapWriter> {
    private MyMapWriter result = new MyMapWriter();
    public void reduce(Text key, Iterable<MyMapWriter> values,
                       Context context
                       ) throws IOException, InterruptedException {
    	result.clear();
      for (MyMapWriter val : values) {
        addAll(val);
      }
      context.write(key, result);
    }
    
    private void addAll(MyMapWriter mapWritable) {
        Set<Writable> keys = mapWritable.keySet();
        for (Writable key : keys) {
            IntWritable fromCount = (IntWritable) mapWritable.get(key);
            if (result.containsKey(key)) {
                IntWritable count = (IntWritable) result.get(key);
                count.set(count.get() + fromCount.get());
            } else {
                result.put(key, fromCount);
            }
        }
    }
    
  }

  public static void main(String[] args) throws Exception {
    Configuration conf = new Configuration();
    Job job = Job.getInstance(conf, "word count");
    FileUtils.deleteDirectory(new File("sample"));
    job.setJarByClass(Stripes.class);
    job.setMapperClass(StripesOccurrenceMapper.class);
    job.setCombinerClass(StripReducer.class);
    job.setReducerClass(StripReducer.class);
    job.setOutputKeyClass(Text.class);
    job.setOutputValueClass(MyMapWriter.class);
    FileInputFormat.addInputPath(job, new Path("/home/anuradha/workspace/Lab4/tweets.txt"));
    FileOutputFormat.setOutputPath(job, new Path("StripesOutput"));
    System.exit(job.waitForCompletion(true) ? 0 : 1);
  }
}
  class MyMapWriter extends MapWritable {
	    @Override
	    public String toString() {
	        StringBuilder result = new StringBuilder();
	        Set<Writable> keySet = this.keySet();

	        for (Object key : keySet) {
	            result.append("{" + key.toString() + " = " + this.get(key) + "}");
	        }
	        return result.toString();
	    }
	}
