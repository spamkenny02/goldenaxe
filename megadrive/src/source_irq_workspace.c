/* Same canonical IRQ body on a caller-owned disposable RAM snapshot.
 * No rollback copy is needed; callers discard the snapshot after rejection. */
#define GAW_IRQ_PRIVATE_WORKSPACE
#define source_irq source_irq_workspace
#include "source_irq.c"
