| Un seul modulateur utile : phase, interpolation et gain natifs exacts.
| Frame de112octets deja etabli par400a8204 ; epilogue natif400a8330.
| Seule l entree ignoree exige poids et rampe nuls.
.text
.globl om_osc
om_osc:
 tst.l %d4
 bne.s .Ltry_b
 tst.l 104(%sp)
 bne.s .Ltry_b
 move.l %fp,%d0
 bne.s .La_setup
 tst.l 108(%sp)
 beq.w .Lold
.La_setup:
 move.l 84(%sp),%a1
 move.l 88(%sp),%d4
 move.l (%a2)+,%d2
 moveq #8,%d0
 bra.w .La
.Ltry_b:
 move.l %fp,%d0
 bne.w .Lold
 tst.l 108(%sp)
 bne.w .Lold
 move.l 84(%sp),%a2
 move.l 88(%sp),%fp
 move.l (%a1)+,%d2
 moveq #8,%d0
 bra.w .Lb
.macro OM_SAMPLE source,weight,phase,gain,ramp
 move.l %d7,%acc1
 mac.l \weight,%d2,%acc1
 add.l \ramp(%sp),\weight
 move.l %acc1,%d2
 swap %d2
 andi.l #255,%d2
 movclr.l %acc1,%d6
 andi.l #65535,%d6
 asl.l %d5,%d6
 move.l (%a5,%d2.l*4),%d3
 move.l 4(%a5,%d2.l*4),%d2
 move.l %d3,%acc0
 mac.l %d6,%d2,%acc0
 msac.l %d6,%d3,%acc0
 add.l \phase,%d7
 andi.l #16777215,%d7
 movclr.l %acc0,%d6
 msac.l %d1,%d6,%acc0
 add.l \gain,%d1
 .if \ramp == 104
 move.l \source,%d2
 .endif
 move.l %d6,(%a3)+
 .if \ramp == 108
 move.l \source,%d2
 .endif
 movclr.l %acc0,%d6
 move.l %d6,(%a0)+
.endm
.La:
 .rept 4
 OM_SAMPLE (%a2)+,%fp,%a1,%d4,108
 .endr
 subq.l #1,%d0
 bne.w .La
 jmp 0x400a8330
.Lb:
 .rept 4
 OM_SAMPLE (%a1)+,%d4,%a2,%fp,104
 .endr
 subq.l #1,%d0
 bne.w .Lb
 jmp 0x400a8330
.Lold:
 jmp om_previous

| Premier operateur : au moins une entree de poids ET rampe nuls.
| Le rendu non module conserve phase en registre, sans relire la pile/sample.
.globl om_first
om_first:
 lea 108(%a0),%a2
 move.l %a4,64(%sp)
 tst.l %d5
 bne.s .Lf_try_b
 tst.l 44(%sp)
 bne.s .Lf_try_b
 move.l %a3,%d3
 bne.s .Lf_a_choose
 tst.l %d7
 beq.s .Lf_dry_setup
.Lf_a_choose:
 move.l %d7,64(%sp)
 move.l 60(%sp),%a5
 move.l #0x7fffffff,%d5
 bra.s .Lf_a_setup
.Lf_try_b:
 move.l %a3,%d3
 bne.w .Lf_old
 tst.l %d7
 bne.w .Lf_old
 move.l 60(%sp),%a6
 move.l #0x7fffffff,%a3
 bra.s .Lf_b_setup
.Lf_dry_setup:
 move.l 60(%sp),%a5
 move.l #0x7fffffff,%d5
 move.l (%a4),%a2
 move.l 108(%a0),%d7
 move.l 48(%sp),%a4
 move.l 56(%sp),%a1
 moveq #8,%d0
 bra.w .Lf_dry
.Lf_a_setup:
 move.l (%a4),%a2
 move.l 108(%a0),%d7
 move.l 48(%sp),%a4
 move.l 56(%sp),%a1
 moveq #8,%d0
 bra.w .Lf_a
.Lf_b_setup:
 move.l (%a4),%a2
 move.l 108(%a0),%d7
 move.l 48(%sp),%a4
 move.l 56(%sp),%a1
 moveq #8,%d0
 bra.w .Lf_b
.macro OM1_BODY unity,rawout
 movclr.l %acc0,%d3
 add.l %d7,%d3
 move.l %d3,%d6
 swap %d6
 andi.l #255,%d6
 swap %d3
 clr.w %d3
 lsr.l #1,%d3
 move.l (%a4,%d6.l*4),%d4
 move.l 4(%a4,%d6.l*4),%d6
 sub.l %d4,%d6
 mac.l \unity,%d4,%acc0
 mac.l %d3,%d6,%acc0
 movclr.l %acc0,%d3
 msac.l %d3,%d2,%acc0
 movclr.l %acc0,%d4
 add.l %d1,%d2
 move.l %d3,(\rawout)+
 move.l %d4,(%a1)+
 add.l %a2,%d7
 andi.l #16777215,%d7
.endm
.Lf_dry:
 .rept 4
 OM1_BODY %d5,%a5
 .endr
 subq.l #1,%d0
 bne.w .Lf_dry
 bra.w .Lf_done
.Lf_a:
 .rept 4
 move.l (%fp)+,%d3
 mac.l %a3,%d3,%acc0
 adda.l 64(%sp),%a3
 OM1_BODY %d5,%a5
 .endr
 subq.l #1,%d0
 bne.w .Lf_a
 bra.w .Lf_done
.Lf_b:
 .rept 4
 move.l (%a5)+,%d3
 mac.l %d5,%d3,%acc0
 add.l 44(%sp),%d5
 OM1_BODY %a3,%fp
 .endr
 subq.l #1,%d0
 bne.w .Lf_b
.Lf_done:
 move.l %d7,108(%a0)
 move.l %a0,%a1
 jmp 0x400a81e8
.Lf_old:
 jmp 0x400a815a
