from Bio import SeqIO


class fastq_pysickle:
    def __init__(self,infile, threshold, phred_type, window_size, outfile):
        # add the arguments to the object for acess from other methods
        self.infile = infile
        self.threshold = threshold
        self.phred_type =phred_type
        self.window_size = window_size
        self.outfile = outfile
        self.min_len = 10 # min length of sequence before it's discarded
        # if the user has specified a filename, redirect stdout to that file
        # outfile will be an empty string if the user hasn't specified anything
        if len(self.outfile) > 0:
            sys.stdout = open(self.outfile)

    
    def calculate_trim_adresses(self):
        '''return the addresses at the 5' and 3' ends at which to trim the sequence'''
        seq_len = len(self.seq)
        if seq_len<self.min_len:
            self.three_addr = -1
            self.five_addr = -1
            return
        if seq_len!=len(self.phred):
            self.three_addr = -1
            self.five_addr = -1
            return
        win_size = int(self.window_size*seq_len)
        if win_size==0:
            win_size = seq_len
        win_total = sum(self.phred[:seq_len])
        win_start=0
        win_total=0
        three_prime_cut = seq_len
        five_prime_cut = 0
        found_five_prime = 0
        i = 0;
        while i <= seq_len - win_size:
            win_ave = float(win_total)/win_size
            if i==0 and win_ave>=self.threshold:
                found_five_prime = 1
            if found_five_prime==0 and win_ave>=self.threshold:
                j = win_start
                while j<win_start+win_size:
                    if self.phred[j]>=self.threshold:
                        five_prime_cut = j
                        break
                    j += 1
                found_five_prime = 1
            if (win_ave<self.threshold or win_start+win_size>seq_len) and found_five_prime == 1:
                j = win_start
                while j<win_start+win_size:
                    if self.phred[j]<self.threshold:
                        three_prime_cut = j
                        if three_prime_cut-five_prime_cut<self.min_len:
                            three_prime_cut = -1
                            five_prime_cut = -1
                            break
                        break
                    j += 1
            win_total -= self.phred[win_start]
            if win_start+win_size<seq_len:
                win_total += self.phred[win_start+win_size]
            win_start += 1
            i += 1
        if found_five_prime==0:
            three_prime_cut = -1
            five_prime_cut = -1
        self.three_addr = three_prime_cut
        self.five_addr = five_prime_cut
        
    def trim(self):
        '''use the calculated addresses to trim the fastq file'''
        self.trimmed_seq = self.seq[self.five_addr:self.three_addr]
        self.trimmed_phred = self.phred[self.five_addr:self.three_addr]

        
    def write_to_output(self):
        '''write out this record to output (file or stdout)'''
        print(self.id)
        print(self.trimmed_seq)
        print('+')
        print(self.trimmed_phred)
        
    def fastq(self):
        '''load the fastq file and pass all the information with quality scores converted to Phred Values'''
        # hard coded to take in only illumina scores but can be extended to work with others
        for record in SeqIO.parse(self.infile, "fastq-illumina"):
            #self.rec = record.format("fastq-illumina")
            self.id = record.id
            self.seq = record.seq
            self.phred = record.letter_annotations["phred_quality"]
            self.calculate_trim_adresses()
#            print(self.three_addr)
#            print(self.five_addr)
            self.trim()
            #self.write_to_output()
    
    
    
    
    
    
