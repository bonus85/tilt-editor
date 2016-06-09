# Tilt brush editor

[Tilt brush documentation](https://docs.google.com/document/d/11ZsHozYn9FnWG7y3s3WAyKIACfbfwb4PbaS8cZ_xjvo/preview)

Inspired by reddit user /u/DrewFitz: [Tilt brush reverse engineering](https://www.reddit.com/r/Vive/comments/4f7q7f/tilt_brush_save_file_reverseengineering_update/). The comment from /u/1pid was also very helpful.

A .tilt file is an uncompressed .zip file with an additional header. The zip contains the following files: A thumbnail PNG, the brush stroke data in a custom binary format (data.sketch), and a JSON metadata file.

Note that the tool is in very early development. The exported .tilt file from a json specification does not work as intended. The stroke is drawn, but all but one vector disappears when the stroke is completed. 

