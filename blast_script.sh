input=$(find /mount/efs/queries/ -name "*.fasta" | head -n $((AWS_BATCH_JOB_ARRAY_INDEX + 1)) | tail -n 1)
filename=$(basename "${input}")
outfile=$filename"_blast_out.txt"

db=$BLAST_DB_NAME

blastp -query  $input -db /mount/efs/blastdb_custom/${db} -out /mount/efs/results/${outfile} -outfmt "6 qaccver stitle pident qcovs length mismatch gapopen qstart qend sstart send evalue bitscore"
