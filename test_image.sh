AWS_BATCH_JOB_ARRAY_INDEX=0
while [ $AWS_BATCH_JOB_ARRAY_INDEX -le 1 ]
do
    docker run --rm  -v /home/sih13/Documents/aws_cazy/blastdb:/mount/efs/blastdb:ro     -v /home/sih13/Documents/aws_cazy/blastdb_custom:/mount/efs/blastdb_custom:ro -v /home/sih13/Documents/aws_cazy/queries:/mount/efs/query:ro     -v /home/sih13/Documents/aws_cazy/results:/mount/efs/results:rw -e AWS_BATCH_JOB_ARRAY_INDEX=$AWS_BATCH_JOB_ARRAY_INDEX blast_cazy
    AWS_BATCH_JOB_ARRAY_INDEX=$((AWS_BATCH_JOB_ARRAY_INDEX + 1))
done