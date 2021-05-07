

# Introduction

  

  

This repository contains code and data for my article "Parallel BLAST against CAZy with AWS Batch".

1. The script "download_cazy_sequence" is for downloading the CAZy sequences.

  

2. blast_script.sh is the entrypoint script.

3. Dockerfile is for building the docker image.

4. The test_image.sh can test whether the docker image has been successfully built.
  
5. The folders are reflections of what should be in the AWS EFS storage. You can also just upload them to your EFS with scp.
  

# Prerequisite

Docker
  

# Run


  
1. Download the CAZy data
```console
python download_cazy_sequence.py  -o [output_fasta_file] -l [record_file]
```
 
2. Put the fasta file into the "fasta" folder and format it into a blastdb. The article describes how. Add the files to the blastdb_custom folder. 

3. Change the environment variable BLAST_DB_NAME to the name of your formatted database. 


4. Upload these files into S3 then to EFS. Or directly to your EFS with scp.
  

## Authors

  

*  **Sixing Huang** - *Concept and Coding*

  

## License

  

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
