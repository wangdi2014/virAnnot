import os.path
from subprocess import call
import logging as log

class Assembly:

	def __init__ (self, args):
		self.check_args(args)
		self.cmd = []
		self.create_cmd()


	def create_cmd (self):
		if self.prog == 'idba':
			self._create_idba_cmd()
		elif self.prog == 'spades':
			self.create_spades_cmd()


	def create_spades_cmd (self):
		self.i1 = self.check_fastq_format(self.i1)
		self.i2 = self.check_fastq_format(self.i2)
		if self.ising != '':
			self.ising = self.check_fastq_format(self.ising)
		cmd = 'metaspades.py' + ' -1 ' + self.i1 + ' -2 ' + self.i2 + ' -o ' + self.wd + '/' + self.sample + '_spades'
		if self.ising != '':
			cmd += ' -s ' + self.ising
		log.debug(cmd)
		self.cmd.append(cmd)

		cmd = 'sed -i \'s,^>NODE_\([0-9]*\)_length_[0-9]*_cov_.*,>' + self.sample + '_\\1,\' ' + self.wd + '/' + self.sample + '_spades' + '/scaffolds.fasta'
		log.debug(cmd)
		self.cmd.append(cmd)
		cmd = 'cp ' + self.wd + '/' + self.sample + '_spades' + '/scaffolds.fasta' + ' ' + self.wd + '/' + self.out
		log.debug(cmd)
		self.cmd.append(cmd)


	def _create_idba_cmd (self):
		self.i1 = self.check_fastq_format(self.i1)
		self.i2 = self.check_fastq_format(self.i2)
		merged_read = os.path.basename(self.i1).split('_')[0] + '_merged.fa'
		cmd = 'fq2fa --merge ' + self.i1 + ' ' + self.i2 + ' ' + merged_read
		log.debug(cmd)
		self.cmd.append(cmd)
		if self.ising != '':
			self.ising = self.check_fasta_format(self.ising)
		cmd = 'idba_ud -r ' + merged_read + ' --num_threads ' + self.n_cpu + ' -o ' + self.wd + '/' + self.sample + '_idba'
		if self.ising != '':
			cmd += ' -l ' + self.ising

		log.debug(cmd)
		self.cmd.append(cmd)
		cmd = 'sed -i \'s,^>scaffold_\([0-9]*\),>' + self.sample + '_\\1,\' ' + self.wd + '/' + self.sample + '_idba' + '/scaffold.fa'
		log.debug(cmd)
		self.cmd.append(cmd)
		cmd = 'cp ' + self.wd + '/' + self.sample + '_idba' + '/scaffold.fa' + ' ' + self.wd + '/' + self.out
		log.debug(cmd)
		self.cmd.append(cmd)


	def check_fasta_format (self, in_file):
		in_file = str(object=in_file)
		self._check_file(in_file)
		out = ''
		if in_file.lower().endswith('.fq') or in_file.lower().endswith('.fastq'):
			out = os.path.splitext(in_file)[0] + '.fa'
			if not self._check_file(out):
				cmd = 'fq2fa' + ' ' + in_file + ' > ' + out
				log.debug(str(cmd))
				self.cmd.append(cmd)
			return out
		else:
			log.debug('Format seems to be fastq.')
			return in_file


	def check_fastq_format (self, in_file):
		in_file = str(object=in_file)
		self._check_file(in_file)
		out = ''
		if in_file.lower().endswith('.fa') or in_file.lower().endswith('.fasta') or in_file.lower().endswith('.fas'):
			out = os.path.splitext(in_file)[0] + '.fq'
			if not self._check_file(out):
				cmd = 'fasta_to_fastq' + ' ' + in_file + ' > ' + out
				log.debug(str(cmd))
				self.cmd.append(cmd)
			return out
		else:
			log.debug('Format seems to be fastq.')
			return in_file


	def check_args (self, args: dict):
		self.execution=1
		if 'sample' in args:
			self.sample = str(args['sample'])
		self.wd = os.getcwd() + '/' + self.sample
		self.cmd_file = self.wd + '/' + self.sample + '_idba_cmd.txt'
		if 'i1' in args:
			self.i1 = self._check_file(self.wd + '/' + args['i1'])
		else:
			self.i1=''
		if 'i2' in args:
			self.i2 = self._check_file(self.wd + '/' + args['i2'])
		else:
			self.i2=''

		if 'ising' in args:
			self.ising = self._check_file(self.wd + '/' + args['ising'])
		else:
			self.ising=''

		if self.i1 == '' and self.i2 == '' and self.ising == '':
			log.critical('At least one read file must be defined.')
			self.execution=0
		if 'prog' in args:
			if args['prog'] == 'idba' or args['prog'] == 'spades':
				self.prog = args['prog']
			else:
				log.critical('Wrong assembly program name.')
				sys.exit(1)
		else:
			log.critical('Program name is mandatory.')
			sys.exit(1)
		if 'n_cpu' in args:
			self.n_cpu = str(args['n_cpu'])
		else:
			self.n_cpu = '1'
		if 'sge' in args:
			self.sge = bool(args['sge'])
		else:
			self.sge = False
		if 'out' in args:
			self.out = args['out']


	def launch (self):
		if(self.sge):
			fw =  open(self.cmd_file, mode='w')
			for el in self.cmd:
				fw.write(el + "\n")
			fw.close()
			qsub_call =   "qsub -wd " + self.wd + " -V -N " + self.sample + '_idba' + ' -pe multithread ' + self.n_cpu +  ' ' + self.cmd_file
			log.debug(qsub_call)
			os.system(qsub_call)
		else:
			for el in self.cmd:
				os.system (el)


	def _check_file (self,f):
		try:
			open(f)
			return f
		except IOError:
			print('File not found ' + f)
			self.execution=0
