#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import cmd
import readline
import sys
import os
import traceback
from src.console_controller import ConsoleController

def try_catch(command, args):
    try:
        if args is not None:
            return command(*args)
        else:
            return command()
    except:
        print("Sorry, that command raised an exception. Here's what I know:\n")
        print(traceback.format_exc())


class GagCmd(cmd.Cmd):

## Setup, loading and saving sessions, exit, etc.

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = "GAG> "
        readline.set_history_length(1000)
        try:
            readline.read_history_file('.gaghistory')
        except IOError:
            sys.stderr.write("No .gaghistory file available...\n")
        self.controller = ConsoleController() 

    def precmd(self, line):
        readline.write_history_file('.gaghistory')
        return cmd.Cmd.precmd(self, line)

    def postcmd(self, stop, line):
        if hasattr(self, 'output') and self.output:
            print self.output
            self.output = None
        return stop

    def parseline(self, line):
        if '|' in line:
            commands = ['']
            quotes = ''
            for c in line:
                if c == '|' and quotes == '':
                    commands[-1] = commands[-1].strip()
                    commands.append('')
                else:
                    if quotes == '' and (c == "'" or c == '"'):
                        quotes = c
                    elif quotes == c:
                        quotes = ''
                    commands[-1] += c
            commands[-1] = commands[-1].strip()
            if len(commands) > 1:
                return 'pipe', commands, line
        return cmd.Cmd.parseline(self, line)

    def do_pipe(self, args):
        buf = None
        for arg in args:
            if buf:
                self.controller.input = buf
            else:
                self.controller.input = ''
            self.output = ''
            self.onecmd(arg)
            if hasattr(self, 'output') and self.output:
                buf = self.output

    def help_barffolder(self):
        print("Usage: barffolder <directory>\n")
        print("Writes gff, fasta and trinotate files to the specified directory.\n")

    def do_barffolder(self, line):
        self.output = try_catch(self.controller.barf_folder, [line])

    def help_loadfolder(self):
        print("\nUsage: loadfolder [directory]")
        print("Reads in a gff, fasta and trinotate file from the specified directory.")
        print("If no directory is supplied, uses current working directory.\n")

    def do_loadfolder(self, line):
        try_catch(self.controller.load_folder, [line])

    def help_exit(self):
        print("Exit this console.\n")

    def do_exit(self, line):
        return True
        
    def help_setfilterarg(self):
        print("\nUsage: modifyfilterarg <filter_name> <filter_arg> <value>\n\nSets a specified filter argument to a specified value.\n")
    
    def do_setfilterarg(self, line):
        try_catch(self.controller.set_filter_arg, line.split(' '))
    
    def help_getfilterarg(self):
        print("\nUsage: getfilterarg <filter_name> <filter_arg> <value>\n\nOutputs the value of the specified filter argument.\n")
    
    def do_getfilterarg(self, line):
        self.output = try_catch(self.controller.get_filter_arg, line.split(' '))
        
    def help_applyfilters(self):
        print("Applies all filters to the genome\n")
    
    def do_applyfilters(self, line):
        try_catch(self.controller.apply_filters, None)
        
    def help_getfilterhelp(self):
        print("\nUsage: getfilterhelp [filter_name]\n\nGets help for a filter. Omit filter name to list info for all filters.\n")
        
    def do_getfilterhelp(self, line):
        self.output = '\n'+try_catch(self.controller.get_filter_help, [line.strip()])+'\n'

    def do_barf(self, line):
        self.output = self.controller.barf(line)

## Assorted utilities

    def help_status(self):
        print("Usage: status\n")
        print("Gives a brief summary of what's in memory\n")

    def do_status(self, line):
        print(try_catch(self.controller.status, None))

    def do_barftofile(self, line):
        try_catch(self.controller.barftofile, [line])


## Manipulate genome

    def help_ducttape(self):
        print("Usage: ducttape\n")
        print("For the genome in memory, does the following:\n")
        print("\t*Renames all 'maker' mRNAs, starting with '<locus_tag>_1000000'\n")
        print("\t*Removes each first CDS segment if its length is less than 4\n")
        print("\t*Verifies all start and stop codons by checking against the actual sequence; creates new features as necessary\n")
        print("\t*Verifies all 'frame' information for coding sequences by running a six-frame translation and checking the\n")
        print("\t protein sequence against the one stored in the annotation file\n")
        print("\t*Removes invalid features -- first eliminating any mRNA with no CDS, then any gene with no mRNAs.\n")

    def do_ducttape(self, line):
        try_catch(self.controller.ducttape, None)

    def do_removemrna(self, line):
        try_catch(self.controller.removemrna, [line])

    def help_removegene(self):
        print("Usage: removegene <gene_id_prefix>\n")
        print("Removes from genome all genes with said gene_id prefix.\n")

    def do_removegene(self, line):
        try_catch(self.controller.remove_gene, [line])

    def help_subsetgenome(self):
        print("Usage: subsetgenome <sequence_id> [other sequence_ids...]\n")
        print("Removes all sequences (and corresponding genes) except those specified\n")

    def do_subsetgenome(self, line):
        self.output = try_catch(self.controller.subset_genome, [line])

    def help_trimregion(self):
        print("Usage: trimregion <seq_id> <start_index> <stop_index>\n")
        print("Removes subsequence from fasta and adjusts indices of features which follow region.\n")

    def do_trimregion(self, line):
        self.output = try_catch(self.controller.trim_region, [line])

    def help_removeseq(self):
        print("Usage: removeseq <seq_id> [-F]\n")
        print("Removes sequence from fasta, only if the sequence contains no features or if the -F option is used.\n")

    def do_removeseq(self, line):
        try_catch(self.controller.remove_seq, [line])

    def help_invalidateregion(self):
        print("Usage: invalidateregion <seq_id> <start> <stop>\n")
        print("Truncates or removes any feature located on region to be invalidated\n")

    def do_invalidateregion(self, line):
        self.output = try_catch(self.controller.invalidate_region, [line])

## Output info to console

    def help_barfgenegff(self):
        print("Usage: barfgenegff <gene_id>\n")
        print("Prints gff entry for corresponding gene to console.\n")

    def do_barfgenegff(self, line):
        self.output = try_catch(self.controller.barf_gene_gff, [line])

    def help_barfseq(self):
        print("Usage: barfseq <seq_id> <start_index> <end_index>\n")
        print("Prints (sub)sequence to console.\n")

    def do_barfseq(self, line):
        self.output = try_catch(self.controller.barf_seq, [line])

    def help_barfcdsseq(self):
        print("Usage: barfcdsseq <mrna>\n")
        print("Prints CDS's whole sequence\n")

    def do_barfcdsseq(self, line):
        self.output = try_catch(self.controller.barf_cds_seq, [line])

    def help_barfgenetbl(self):
        print("TODO")   # TODO

    def do_barfgenetbl(self, line):
        self.output = try_catch(self.controller.barf_gene_tbl, [line])

    def help_stats(self):
        print("Usage: stats\n")
        print("Prints summary statistics about original genome (from file)" +\
                " and modified genome (filters applied). May take a moment to run.")

    def do_stats(self, line):
        self.output = try_catch(self.controller.stats, None)

## Output info to file

    def help_writetbl(self):
        print("Usage: writetbl <file_name>\n")
        print("Write a sweet feature table to the specified file.\n")

    def do_writetbl(self, line):
        self.output = try_catch(self.controller.write_tbl, [line])


########################################################################

def get_greeting():
    logo = "................................................................   .       .    \n........................................,,........................  .... .  ....\n..............~++=:,............... ..=OMNZ:....... ....... ..:=?77I=,... .. ...\n...........:7DMMMMMMD7:............. ~DMMMMZ...............=$DMMMMMMMM8+........\n.........:7NMMMMMMMMMMN7,............$MMMMMN=. ....... ..~ZMMMMMMMMMMMMZ,.   ...\n........?NMMMNZ+~+IONMMN?....... ...INMMNMMMI .. .......INMMMDZ?~,,:+I?:. . .  .\n.......+NMMN7:  ... :?$I: .........INMMNZMMMZ.........:$MMMD?........   ........\n......:8MMM?..........  ..........7MMMD+=NMM8,... .. :OMMMO~ ...................\n......7MMMZ,.....................7MMMD= ,8MMM? ......ZMMMZ,.....................\n.....:8MMN+....................,$MMMN+.. IMMMO......~NMMD~ ....,+$ZI+==~,.......\n.....~DMMD~....~7OZ$Z8NNZ:....+DMMMD$I?~:~DMMN+. ...+NMM8......IMMMMMMMMO: ..  .\n......$MMM8:. ,OMMMMMMMMN=...INMMN$$MMMMMMMMMMZ.....~DMMMI.....~8MMMMMMMZ: ...  \n......,ZMMMD?,.?NMMMMMNZ~. .INMMD+.=ONMMMMMMMMN~. ...+DMMM$:.  ..,=$MMMD: ...   \n.......,$MMMMM87+IONMMMI...?NMMN= ....:=+??OMMM$..... =8MMMM87=,.,+8MMMZ.  .   .\n.........+8MMMMMMMMMMMO~. ~DMMN?...... . ..=NMM$.......:$NMMMMMMNMMMMMO:.... . .\n...........:I8NMMMMNO+,...:OMD?. ....... ...+Z7~.........:I8NMMMMMMMDI,    .   .\n............. .:~~:. ......,,,.. . ... . . . ..  . ... . .  .~?7$7?~.        .  \n................................ . . .   . . .   . . .   . . .         .       .\n................. ....... ......   . .     . .     . .     . .         .       ."
    message = "\nWelcome to the GAG console!\n"
    message += "Type 'help' for available commands.\n"

    return logo + message

if __name__ == '__main__':
    GagCmd().cmdloop(get_greeting())
