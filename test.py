import itertools

octopus_shapes = ["Spheroid", "Torus", "Torus2"]

combinations = itertools.combinations_with_replacement(octopus_shapes, 4)
# print(combinations)
# print(type(combinations))
combin_list = list(combinations)
print(combin_list)

print(list(combinations))

for comb in combinations:
    print(comb[0])