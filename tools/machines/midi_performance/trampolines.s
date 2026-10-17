| Huit octets de prologue verifies, puis retour a la fonction native chargee.
 .text
 .globl bp_step_original,bp_clock_original,bp_enc_original
bp_step_original:
 .long 0,0
 jmp 0xf0010000
bp_clock_original:
 .long 0,0
 jmp 0xf0010000
bp_enc_original:
 .long 0,0
 jmp 0xf0010000
