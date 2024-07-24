-- Create the games table
   CREATE TABLE games (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       app_id TEXT,
       name TEXT
   );

   -- Create the settings table
   CREATE TABLE settings (
       time_per_credit REAL,
       video_path TEXT,
       reset_image_path TEXT,
       restart_image_path TEXT
   );

   -- Insert some sample data based on visible content
   INSERT INTO settings (time_per_credit, video_path, reset_image_path, restart_image_path)
   VALUES (1.0, 'C:\Users\Bamigos\Desktop\metacade try\video.mp4',
           'C:\Users\Bamigos\Desktop\metacade try\resetheadset.png',
           'C:\Users\Bamigos\Desktop\metacade try\restartsteamvr.png');