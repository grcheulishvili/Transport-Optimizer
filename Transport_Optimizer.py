from ortools.sat.python import cp_model


output = open("Satransporto_ganrigi.txt", "w")

def main():
    
    mdzgolebis_n = 10 
    xazta_n = 4
    dgeebi_n = 5 
    yvela_mdzgoli = range(mdzgolebis_n)
    yvela_xazi = range(xazta_n)
    yvela_dge = range(dgeebi_n)

   
    model = cp_model.CpModel()

    # ცვლის მონაცემები.
    # cvlebi[(n, d, s)]: მძღოლი 'n' მუშაობს 's' ხაზზე 'd' დღეს.
    cvlebi = {}
    for n in yvela_mdzgoli:
        for d in yvela_dge:
            for s in yvela_xazi:
                cvlebi[(n, d,
                        s)] = model.NewBoolVar('shift_n%id%is%i' % (n, d, s))

    # ხაზი მიენიჭება შესაბამის ერთ მძღოლს
    for d in yvela_dge:
        for s in yvela_xazi:
            model.AddExactlyOne(cvlebi[(n, d, s)] for n in yvela_mdzgoli) # AddExactlyOne

    # თითო მძღოლი ერთ ხაზზე მუშაობს
    for n in yvela_mdzgoli:
        for d in yvela_dge:
            model.AddAtMostOne(cvlebi[(n, d, s)] for s in yvela_xazi)

    # ოპტიმალური გამოსავალია თუ ყველა მძღოლი თანაბრად იმუშავებს,
    # მაგრამ თუ მოხდა ისე, სამუშაო დღეები მეტია მძღოლებზე,
    # მაშინ ზოგიერთ მძღოლს მეტის მუშაობა მოუწევს
    min_cvlebi_mdzgolze = (xazta_n * dgeebi_n) // mdzgolebis_n
    if xazta_n * dgeebi_n % mdzgolebis_n == 0:
        max_cvlebi_mdzgolze = min_cvlebi_mdzgolze
    else:
        max_cvlebi_mdzgolze = min_cvlebi_mdzgolze + 1
    for n in yvela_mdzgoli:
        namushevar_dgeebi = []
        for d in yvela_dge:
            for s in yvela_xazi:
                namushevar_dgeebi.append(cvlebi[(n, d, s)])
        model.Add(min_cvlebi_mdzgolze <= sum(namushevar_dgeebi))
        model.Add(sum(namushevar_dgeebi) <= max_cvlebi_mdzgolze)

    solver = cp_model.CpSolver()
    solver.parameters.linearization_level = 0
    # ამონახსნთა დანომვრა
    solver.parameters.enumerate_all_solutions = True


    class MdzgolebisAmoxsna(cp_model.CpSolverSolutionCallback):
        
        def __init__(self, cvlebi, mdzgolebis_n, dgeebi_n, xazta_n, limit):
            cp_model.CpSolverSolutionCallback.__init__(self)
            self._cvlebi = cvlebi
            self._mdzgolebis_n = mdzgolebis_n
            self._dgeebi_n = dgeebi_n
            self._xazta_n = xazta_n
            self._amonaxsnta_n = 0
            self._amonaxsnta_limit = limit

        def on_solution_callback(self):
            self._amonaxsnta_n += 1
            print("----------------------------------", file=output)

            print('Amonaxsni N%i' % self._amonaxsnta_n, file=output)
            for d in range(self._dgeebi_n):
                print('Dge %i' % d, file=output)
                for n in range(self._mdzgolebis_n):
                    mushaobs = False
                    for s in range(self._xazta_n):
                        if self.Value(self._cvlebi[(n, d, s)]):
                            mushaobs = True
                            print('  Mdzgoli %i mushaobs N%i xazze' % (n, s), file=output)
                    if not mushaobs:
                        print('  Mdzgoli {} ar mushaobs'.format(n), file=output)
            if self._amonaxsnta_n >= self._amonaxsnta_limit:
                print('\nAnalizi morcha %i amoxsnis shemdeg' % self._amonaxsnta_limit, file=output)
                self.StopSearch()

        def amonaxsnta_n(self):
            return self._amonaxsnta_n

    # პირველი 5 ამონახსნის გამოტანა
    amonaxsnta_limit = 5
    amonaxsni = MdzgolebisAmoxsna(cvlebi, mdzgolebis_n,
                                                    dgeebi_n, xazta_n,
                                                    amonaxsnta_limit)

    solver.Solve(model, amonaxsni)

    # საწყისი მონაცემები
    print('\n---------------------', file=output)
    print('  - Mdzgolebis Raodenoba     : {}'.format(mdzgolebis_n), file=output)
    print('  - xazta raodenoba      :{}'.format(xazta_n),file=output)
    print('  - dgeebis raodenoba    : {}'.format(dgeebi_n), file=output)
    print('---------------------', file=output)
    # სტატისტიკა
    print('Statistics', file=output)
    print('  - konfliqti      : %i' % solver.NumConflicts(), file=output)
    print('  - ganshtoeba          : %i' % solver.NumBranches(), file=output)
    print('  - gamotvlis dro      : %f s' % solver.WallTime(), file=output)
    print('  - napovni amonaxsnebi: %i' % amonaxsni.amonaxsnta_n(), file=output)


if __name__ == '__main__':
    main()

output.close()
