import os.path
from subprocess import call
import logging as log
import sys

class Ecsv2excel:

	def __init__ (self, args):
		self.check_args(args)
		self.cmd = []
		self.create_cmd()


	def create_cmd (self):
		cmd = 'ecsv2excel.pl'
		for c in self.blast_files:
			cmd += ' -b ' + str(c)
		if self.r != '':
			cmd += ' -r ' + self.r
		cmd += ' -o ' + self.out
		log.debug(cmd)
		self.cmd.append(cmd)


	def check_args (self, args: dict):
		self.execution=1
		self.sample = args['sample']
		self.wd = os.getcwd() + '/' + self.sample
		self.cmd_file = self.wd + '/' + 'ecsv2excel_cmd.txt'
		if 'out' in args:
			self.out = self.wd + '/' + args['out']
		if 'sge' in args:
			self.sge = bool(args['sge'])
		else:
			self.sge = False
		self.blast_files = []
		for i in range(1, 10, 1):
			opt_name = 'b' + str(object=i)
			if opt_name in args:
				if os.path.exists(self.wd + '/' + args[opt_name]):
					self.blast_files.append(self.wd + '/' + args[opt_name])
		if 'r' in args:
			if os.path.exists(self.wd + '/' + args['r']):
				self.r = self._check_file(self.wd + '/' + args['r'])
			else:
				self.r = ''
		else:
			self.r = ''
		if len(self.blast_files) == 0:
			self.execution=0
		if 'n_cpu' in args:
			self.n_cpu = str(args['n_cpu'])
		else:
			self.n_cpu = '1'



	def _check_file (self,f):
		try:
			open(f)
			return f
		except IOError:
			print('File not found ' + f)
			sys.exit(1)
