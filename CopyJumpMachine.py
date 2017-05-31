#!/usr/bin/env python3
'''A bytecode interpreter. Possible instructions are of assignment or jump type.'''

class BitPrinter: # pylint: disable=too-few-public-methods
    '''Prints a bit and a byte.'''
    def __init__(self):
        self.out_sequence = []

    def print(self, bit):
        '''Adds a bit to the output.'''
        assert bit == 0 or bit == 1
        self.out_sequence.append(bit)

        print('out:', bit)

        if len(self.out_sequence) == 8:
            num = 0
            pos = 1
            for iter_bit in self.out_sequence:
                num += pos * iter_bit
                pos *= 2
            print('n:', num)
            self.out_sequence = []

def run_code(code, bit_printer, memory):
    '''Runs some source code.'''

    def init_memory(mem):
        '''Initializes memory.
        #memory[0] = 0 #constant source of zeroes during bit copy (mov)
        #memory[1] = 1 #constant source of ones during bit copy (mov)'''
        return [0, 1] + mem

    mem = init_memory(memory)

    def parse(code):
        '''Parses source code.'''
        lines = []
        labels = {}
        for line in code.split('\n'):
            operands = line.split(' ')
            if operands[0] != 'l': # exclude labels (lines with label)
                lines.append(line)
            elif operands[0] == 'l':
                labels[operands[1]] = len(lines)
        labels['end'] = len(lines)
        return lines, labels

    lines, labels = parse(code)

    def execute(lines, labels, bit_printer):
        '''Runs some byte code.'''

        def read(src): # read from address
            '''Reads a bit from an address.'''
            try:
                src = int(src)
                value = mem[src]
            except ValueError:
                if src == 'in':
                    while True:
                        try:
                            value = int(input('bit? '))
                            if value in (0, 1):
                                break
                        except ValueError:
                            pass
            return value

        def write(dst, src, bit_printer): # write to address
            '''Writes a bit copying from source address to destination address.'''
            try:
                dst = int(dst)
                mem[dst] = src
            except ValueError:
                if dst == 'out':
                    bit_printer.print(src)

        def jump(cline, instruction_pointer, labels): # pylint: disable=too-many-arguments
            '''Handles Jump instructions.'''
            if len(cline) == 2: # unconditional jump
                new_instruction_pointer = cline[1]

            elif len(cline) == 3: # conditional jump
                bit = read(cline[1])
                assert bit == 0 or bit == 1
                if bit == 0:
                    new_instruction_pointer = 'next'
                elif bit == 1:
                    new_instruction_pointer = cline[2]

            elif len(cline) == 4: # 2-conditional jump
                bit = read(cline[1])
                assert bit == 0 or bit == 1
                if bit == 0:
                    new_instruction_pointer = cline[2]
                elif bit == 1:
                    new_instruction_pointer = cline[3]

            if new_instruction_pointer == 'next':
                instruction_pointer += 1
            else:
                try:
                    instruction_pointer = int(new_instruction_pointer)
                except ValueError:
                    instruction_pointer = labels[new_instruction_pointer]

            return instruction_pointer

        executable_lines = list(map(lambda s: s.split(' '), lines))
        instruction_pointer = 0

        while instruction_pointer < len(lines):
            cline = executable_lines[instruction_pointer]

            if cline[0] == 'j': # parse jump

                instruction_pointer = jump(cline, instruction_pointer, labels)

            elif cline[0] == 'm': # parse move

                dst, src = cline[1], cline[2]

                got = read(src)
                write(dst, got, bit_printer)
                instruction_pointer += 1

            else:
                print('current line(cline) is not a valid instruction:', cline)

    execute(lines, labels, bit_printer)

# Move {copy_to_memory_address} {copy_from_memory_address}
# Jump {label_to_jump_to}
# Jump {condition_at_memory_address} {label_to_jump_to}
# Label {jump_destination_label}

PROGRAM_NOT_GATE = '''j in zero
m out 1
j end
l zero
m out 0'''

PROGRAM_OR_GATE = '''j in one_x
j in out_one
m out 0
j end
l one_x
m 2 in
m out 1
j end
l out_one
m out 1'''

'''
n = 0
while True:
    print(n)
    if n == 255:
        break
    else:
        n += 1
'''
PROGRAM_INTEGER_COUNTER = '''l loop
m out 2
m out 3
m out 4
m out 5
m out 6
m out 7
m out 8
m out 9
j 2 increment next
j 3 increment next
j 4 increment next
j 5 increment next
j 6 increment next
j 7 increment next
j 8 increment next
j 9 increment next
j end
l increment
j 2 0is0 0is1
l 0is0
m 2 1
j loop
l 0is1
m 2 0
j 3 1is0 1is1
l 1is0
m 3 1
j loop
l 1is1
m 3 0
j 4 2is0 2is1
l 2is0
m 4 1
j loop
l 2is1
m 4 0
j 5 3is0 3is1
l 3is0
m 5 1
j loop
l 3is1
m 5 0
j 6 4is0 4is1
l 4is0
m 6 1
j loop
l 4is1
m 6 0
j 7 5is0 5is1
l 5is0
m 7 1
j loop
l 5is1
m 7 0
j 8 6is0 6is1
l 6is0
m 8 1
j loop
l 6is1
m 8 0
j 9 7is0 7is1
l 7is0
m 9 1
j loop
l 7is1
m 9 0
j loop'''

if __name__ == '__main__':

    BIT_PRINTER = BitPrinter()
    MEMORY = [0 for i in range(1024*8)]
    run_code(PROGRAM_INTEGER_COUNTER, BIT_PRINTER, MEMORY)
