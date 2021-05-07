FROM ncbi/blast
ENV BLAST_DB_NAME="cazy_2021_05_02"
COPY blast_script.sh /tmp/blast_script.sh
RUN chmod +x /tmp/blast_script.sh
ENTRYPOINT /tmp/blast_script.sh