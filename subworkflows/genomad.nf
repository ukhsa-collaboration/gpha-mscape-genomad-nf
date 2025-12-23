process fastq_to_fasta {
    container "community.wave.seqera.io/library/pip_pyfastx:c1d255a74c4291f8"

    //publishDir "fasta", mode: "copy"
    
    input:
    tuple val(climb_id), path(fastq)

    output:
    path "*.fasta"

    script:
    """
    pyfastx fq2fa ${fastq} > ${fastq}.fasta
    """
}

process run_genomad {
    label "process_fair"
    
    container "community.wave.seqera.io/library/genomad:1.11.2--1e14efa5dfbf0dc3"

    publishDir "genomad_results/${unique_id}/", mode: 'copy'

    input:
    file fasta

    output:
    path "**"
    
    script:
    """
        genomad                       \
            end-to-end                \
            --cleanup                 \
            --splits ${{ task.attempt * 25 }}        \
            ${fasta}                  \
            ${fasta}.genomad          \
            ${params.genomad_db}
    """
}

workflow FASTQGZ_TO_GENOMAD{
    take:
    single_end_ch
    
    main:
    single_end_ch | fastq_to_fasta | run_genomad
} 