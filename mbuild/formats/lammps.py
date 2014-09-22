from mdtraj.utils import in_units_of


def save_lammps(traj, step=-1, optional_nodes=None, filename='data.mbuild',
                unit_set='real'):
    """Output a Trajectory as a LAMMPS data file.

    Args:
        traj (md.Trajectory): The Trajectory to be output.
        filename (str, optional): Path of the output file.

    """
    _radians_unit = 'radians'
    _degrees_unit = 'degrees'
    if unit_set == 'real':
        _distance_unit = 'angstroms'
        _velocity_unit = 'angstroms/femtosecond'
        _energy_unit = 'kilocalories/mole'
        _mass_unit = 'grams/mole'
        _charge_unit = 'elementary_charge'
        _mole_unit = 'mole'
    else:
        raise Exception("Unsupported unit set specified: {0}".format(unit_set))

    directives_to_write = list()
    mass_list = list()
    mass_list.append('\n')
    mass_list.append('Masses\n')
    mass_list.append('\n')

    atom_list = list()
    atom_list.append('\n')
    atom_list.append('Atoms\n')
    atom_list.append('\n')

    numeric_atom_types = dict()
    atom_type_n = 1
    for chain in traj.top.chains:
        for atom in chain.atoms:
            if atom.name not in numeric_atom_types:
                numeric_atom_types[atom.name] = atom_type_n
                mass = in_units_of(atom.element.mass, 'grams/moles', _mass_unit)
                mass_list.append('{0:d} {1:8.4f}\n'.format(atom_type_n, mass))
                atom_type_n += 1

            x, y, z = in_units_of(traj.xyz[step][atom.index], 'nanometers',
                                  _distance_unit)
            entry = '{0:-6d} {1:-6d} {2:-6d} {3:5.8f} {4:8.5f} {5:8.5f} {6:8.5f}\n'.format(
                atom.index + 1, chain.index + 1, numeric_atom_types[atom.name],
                0.0, x, y, z)
            atom_list.append(entry)

    directives_to_write.append(mass_list)
    directives_to_write.append(atom_list)

    # NOTE: Bond writing should technically be optional for LAMMPS
    bond_list = list()
    bond_list.append('\n')
    bond_list.append('Bonds\n')
    bond_list.append('\n')

    # TODO: Reduce the bond/angle/dihedral/improper stuff to one chunk of code
    #       that prints n atoms.
    numeric_bond_types = dict()
    bond_type_n = 1
    for bond_n, bond in enumerate(traj.top.ff_bonds):
        if bond.kind not in numeric_bond_types:
            numeric_bond_types[bond.kind] = bond_type_n
            bond_type_n += 1
        bond_list.append('{0:-6d} {1:6d} {2:6d} {3:6d}\n'.format(
            bond_n + 1, numeric_bond_types[bond.kind],
            bond.atom1.index + 1, bond.atom2.index + 1))
    n_bonds = bond_n + 1
    directives_to_write.append(bond_list)

    angle_list = list()
    angle_list.append('\n')
    angle_list.append('Angles\n')
    angle_list.append('\n')

    numeric_angle_types = dict()
    angle_type_n = 1
    for angle_n, angle in enumerate(traj.top.ff_angles):
        if angle.kind not in numeric_angle_types:
            numeric_angle_types[angle.kind] = angle_type_n
            angle_type_n += 1
        angle_list.append('{0:-6d} {1:6d} {2:6d} {3:6d} {4:6d}\n'.format(
            angle_n + 1, numeric_angle_types[angle.kind],
            angle.atom1.index + 1, angle.atom2.index + 1, angle.atom3.index + 1))
    n_angles = angle_n + 1
    directives_to_write.append(angle_list)

    dihedral_list = list()
    dihedral_list.append('\n')
    dihedral_list.append('Dihedrals\n')
    dihedral_list.append('\n')

    numeric_dihedral_types = dict()
    dihedral_type_n = 1
    for dihedral_n, dihedral in enumerate(traj.top.ff_dihedrals):
        if dihedral.kind not in numeric_dihedral_types:
            numeric_dihedral_types[dihedral.kind] = dihedral_type_n
            dihedral_type_n += 1
        dihedral_list.append('{0:-6d} {1:6d} {2:6d} {3:6d} {4:6d} {5:6d}\n'.format(
            dihedral_n + 1, numeric_dihedral_types[dihedral.kind],
            dihedral.atom1.index + 1, dihedral.atom2.index + 1,
            dihedral.atom3.index + 1, dihedral.atom4.index + 1))
    n_dihedrals = dihedral_n + 1
    directives_to_write.append(dihedral_list)

    n_impropers = 0

    print numeric_atom_types
    print numeric_bond_types
    print numeric_angle_types
    print numeric_dihedral_types

    with open(filename, 'w') as f:
        f.write('{0} atoms\n'.format(traj.n_atoms))
        f.write('{0} bonds\n'.format(n_bonds))
        f.write('{0} angles\n'.format(n_angles))
        f.write('{0} dihedrals\n'.format(n_dihedrals))
        f.write('{0} impropers\n'.format(n_impropers))
        f.write('\n')

        box = traj.boundingbox(step)
        box.mins = in_units_of(box.mins, 'nanometers', _distance_unit)
        box.maxes = in_units_of(box.mins, 'nanometers', _distance_unit)
        f.write(
            '{0:10.6f} {1:10.6f} xlo xhi\n'.format(box.mins[0], box.maxes[0]))
        f.write(
            '{0:10.6f} {1:10.6f} ylo yhi\n'.format(box.mins[1], box.maxes[1]))
        f.write(
            '{0:10.6f} {1:10.6f} zlo zhi\n'.format(box.mins[2], box.maxes[2]))

        for directive in directives_to_write:
            for entry in directive:
                f.write(entry)


if __name__ == "__main__":
    from mbuild.examples.ethane.ethane import Ethane

    ethane = Ethane()
    ethane = ethane.to_trajectory()
    ethane.top.find_forcefield_terms()
    save_lammps(ethane, filename='data.ethane')
