# one of the funtions mentioned in https://stackoverflow.com/questions/9835762/how-do-i-find-the-duplicates-in-a-list-and-create-another-list-with-them
def rem_dup(it):
    seen = set()
    uniq = []
    for x in it:
        if x not in seen:
            uniq.append(x)
            seen.add(x)
    return (uniq)


#remove any special charachters from the keyword
# ''.join(filter(str.isalnum, 'security—the!23'))
#>>> securitythe23

def remove_special_char(s):
   a = ''.join(filter(str.isalnum, s))
   return (a)

def remove_numbers_fromStr(s):
    return ''.join([i for i in s if not i.isdigit()])
