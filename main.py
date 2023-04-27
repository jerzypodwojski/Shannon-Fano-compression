def gen_weights_array(data):
    alfabet = []

    for i in data:
        if i not in alfabet:
            alfabet.append(i)

    ile_liter = [0] * len(alfabet)
    for i in range(len(data)):
        for j in range(len(alfabet)):
            if alfabet[j] == data[i]:
                ile_liter[j] += 1

    zip_array = zip(ile_liter, alfabet)
    zip_array = sorted(zip_array)

    sorted_weights = [y for y, x in zip_array]
    sorted_alphabet = [x for y, x in zip_array]

    return sorted_weights[::-1], sorted_alphabet[::-1]


def binary_tree(weights, alphabet, alphabetArray, finalArray):
    chances = 0
    when_slice = 0
    for i in range(len(weights)):
        chances += weights[i]
    for i in range(len(weights)):
        when_slice2 = when_slice
        when_slice += (weights[i])
        if chances / 2 >= when_slice:
            continue
        else:
            if abs(chances / 2 - when_slice) > abs(chances / 2 - when_slice2):
                i -= 1
            if i == 0:
                i = 1
            if len(weights) == 1:
                finalArray[alphabetArray.index(alphabet[0])] += "0"
                return finalArray
            if len(weights) == 2:
                finalArray[alphabetArray.index(alphabet[0])] += "0"
                finalArray[alphabetArray.index(alphabet[1])] += "1"
                return finalArray
            else:
                left_alphabet = alphabet[:i]
                right_alphabet = alphabet[i:]
                left_weights = weights[:i]
                right_weights = weights[i:]
                for x in range(i):
                    finalArray[alphabetArray.index(left_alphabet[x])] += "0"
                for z in range(len(right_alphabet)):
                    finalArray[alphabetArray.index(right_alphabet[z])] += "1"
                binary_tree(left_weights, left_alphabet, alphabetArray, finalArray)
                binary_tree(right_weights, right_alphabet, alphabetArray, finalArray)
                return finalArray


def create_header(alphabet, alphabet_values):
    header = ""
    if len(str(len(alphabet))) < 3:
        header += "0" * (4 - len(str(len(alphabet))))
    header += str(len(alphabet))

    for i in alphabet_values:
        if len(str(len(i))) < 2:
            header += "0" * (2 - len(str(len(i))))
        header += str(len(i))

    for i in range(len(alphabet)):
        header += alphabet[i]

    for i in range(len(alphabet_values)):
        if len(str(int(alphabet_values[i], 2))) < 10:
            header += "0" * (10 - len(str(int(alphabet_values[i], 2))))
        header += str(int(alphabet_values[i], 2))

    head_len = len(header)
    header = str(head_len) + header
    if len(str(head_len)) < 8:
        header = "0" * (8 - len(str(head_len))) + header

    return header


def prepare_file(alphabet, alphabet_values, data):
    new_data = ""
    for i in data:
        for j in range(len(alphabet)):
            if alphabet[j] == i:
                new_data += alphabet_values[j]
    return new_data


def translate_header(header):
    letters_num = int(header[:4])
    len_values = []
    alphabet = []
    alphabet_values = []

    for i in range(4, (letters_num * 2) + 4, 2):
        len_values.append(int(header[i:i + 2]))

    for i in range(letters_num * 2 + 4, letters_num * 3 + 4):
        alphabet.append(header[i])

    k = 0
    for i in range(letters_num * 3 + 4, len(header), 10):
        alphabet_value = bin(int(header[i:i + 10]))[2:]

        if len_values[k] > len(alphabet_value):
            alphabet_value = "0" * (len_values[k] - len(alphabet_value)) + alphabet_value

        k += 1
        alphabet_values.append(alphabet_value)

    return alphabet, alphabet_values


def translate_file(alphabet, alphabet_values, data):
    code_dict = {v: k for k, v in zip(alphabet, alphabet_values)}

    current_code = ""
    decoded_output = ""

    for bit in data:
        current_code += bit
        if current_code in code_dict:
            decoded_output += code_dict[current_code]
            current_code = ""

    return decoded_output


if __name__ == '__main__':
    # --- compress ---
    with open('pan-tadeusz.txt', 'r', encoding="utf8") as f_in:
        file = f_in.read()
    f_in.close()

    open('new-data.beka', 'w').close()
    open('decompressed-data.txt', 'w').close()

    # building binary tree using Shannon Fano coding
    weightsArray1, alphabetArray1 = gen_weights_array(file)
    alphabetArray2 = alphabetArray1.copy()
    finalArray1 = [""] * len(alphabetArray1)
    finalArray1 = (binary_tree(weightsArray1, alphabetArray1, alphabetArray2, finalArray1))

    # creating header
    head = create_header(alphabetArray1, finalArray1)
    head = head.encode('utf-8')

    # swap binary values into bytes
    file = prepare_file(alphabetArray1, finalArray1, file)
    file = bytearray(int(file[i:i + 8], 2) for i in range(0, len(file), 8))

    with open("new-data.beka", "wb") as new_file:
        new_file.write(head)
        new_file.write(bytes(file))
    new_file.close()

    # --- decompress ---
    with open('new-data.beka', 'rb') as f_in:
        head_length = int(f_in.read(8))
        head = f_in.read(head_length + 24).decode(encoding='utf-8')
        compressed_data = f_in.read()
    f_in.close()

    # change bytes to bits
    binary_string = ''.join(format(i, '08b') for i in compressed_data)

    # translate data based on information in header
    new_alphabet, new_alphabet_values = translate_header(head)
    translated_data = translate_file(new_alphabet, new_alphabet_values, binary_string)

    with open("decompressed-data.txt", "w", encoding='utf-8') as new_file:
        new_file.write(translated_data)
    new_file.close()
