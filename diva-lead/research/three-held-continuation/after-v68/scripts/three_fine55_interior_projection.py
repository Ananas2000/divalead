"""Interior correction of existing fine-phase values, retaining all audio limits."""
def repair_fine55(rows,best,compute,probe,lower,upper,guards,select_interior=None):
    import numpy as np
    from project_three_existing_vector import project
    choices=[r for r in rows if r['weighted_score']<=best+1e-12 and r['minimum_constraint']>=-5e-4]
    if not choices:return dict(attempted=False,reason='no better near-feasible fine55 point')
    chosen=min(choices,key=lambda r:r['weighted_score'])
    point,report=project(chosen['fine_phase_offsets'],compute,lower,upper,[list(guards).index('whole'),len(guards)+1])
    report.update(attempted=True,source_tone=chosen['weighted_score'],existing55_fine_phase_values_only=True)
    if point is None:return report
    _,row,con=compute(point)
    if con.min()<=2e-7 or row['weighted_score']>=rows[0]['weighted_score']-1e-6:
        report.update(accepted_numeric=False,reason='interior correction did not improve feasible tone')
        return report
    if select_interior is not None:
        select_interior(point)
    elif row['weighted_score']<best-1e-6:
        probe(point)
    else:
        report.update(accepted_numeric=False,reason='caller has no guarded-candidate selection callback')
        return report
    report.update(accepted_numeric=True,projected_tone=row['weighted_score'],minimum_constraint=float(np.min(con)),requires_full_actual_proof=True)
    return report
