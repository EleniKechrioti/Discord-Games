WORD_LENGTH = 5

def check_guess(guess, target):
    """
    Ελέγχει τη λέξη-εικασία του παίκτη σε σύγκριση με τη λέξη-στόχο.

    Για κάθε γράμμα:
    - Αν είναι στη σωστή θέση, επιστρέφει 'correct'.
    - Αν υπάρχει στη λέξη αλλά σε άλλη θέση, επιστρέφει 'present'.
    - Αν δεν υπάρχει καθόλου, επιστρέφει 'absent'.
    Args:
        guess (str): Η λέξη-εικασία του παίκτη.
        target (str): Η σωστή λέξη-στόχος που πρέπει να βρεθεί.
    Returns:
        list[str]: Λίστα με αποτελέσματα για κάθε γράμμα ('correct', 'present', 'absent').
    """

    result = ['absent'] * len(guess)
    target_list = list(target)

    for i in range(len(guess)):
        if guess[i] == target[i]:
            result[i] = 'correct'
            target_list[i] = None

    for i in range(len(guess)):
        if result[i] == 'correct':
            continue
        if guess[i] in target_list:
            result[i] = 'present'
            target_list[target_list.index(guess[i])] = None

    return result


def color_guess_row(self, row, result):
    """
    Ενημερώνει τα χρώματα των κελιών της σειράς που μόλις παίχτηκε,
    σύμφωνα με το αποτέλεσμα κάθε γράμματος.

    Πιο συγκεκριμένα:
    - Πράσινο για σωστή θέση (correct).
    - Χρυσό για σωστό γράμμα σε λάθος θέση (present).
    - Γκρι για λάθος γράμμα (absent).

    Args:
        self: Η κλάση WordleGame που περιέχει τα labels.
        row (int): Η σειρά του grid που ενημερώνεται.
        result (list[str]): Η λίστα αποτελεσμάτων από τη συνάρτηση check_guess.
    """

    for i in range(WORD_LENGTH):
        if result[i] == "correct":
            bg = 'green'
            fg = 'white'
        elif result[i] == "present":
            bg = 'gold'
            fg = 'black'
        else:
            bg = 'gray'
            fg = 'white'
        self.labels[row][i].config(bg=bg, fg=fg)