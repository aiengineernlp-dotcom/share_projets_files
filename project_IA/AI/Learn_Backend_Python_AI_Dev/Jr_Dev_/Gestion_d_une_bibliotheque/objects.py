"#instanciation (Creation des objects)"
import classes

#object Librairie
book_1 = classes.Book('Titre_book1','Auteur_book_1',1,True)
book_2 = classes.Book('Titre_book2','Auteur_book_2',2,True)
book_3 = classes.Book('Titre_book3','Auteur_book_3',3,True)
book_4 = classes.Book('Titre_book4','Auteur_book_4',4,True)
book_5 = classes.Book('Titre_book5','Auteur_book_5',5,True)
list_book = [book_1,book_2,book_3]

#object User
user1 = classes.User(1,'User_1','User_1@gmail.com','pass1')
user2 = classes.User(2,'User_2','User_2@gmail.com','pass2')
user3 = classes.User(3,'User_3','User_3@gmail.com','pass3')
user4 = classes.User(4,'User_4','User_4@gmail.com','pass4')

#object Librarie
library = classes.Library()


"#Interaction entre les objects"
print('==================Ajouter livres ===============================================================================================\n')

library.add_books(list_book)
library.add_books(book_5)

print('==================Emprunter_livre ===============================================================================================\n')

user1.emprunter_livr(list_book,)
user1.emprunter_livr(book_4,)
user4.emprunter_livr(book_5,)
print('==================rendre_livr ===============================================================================================\n')
user1.rendre_livr(library)




print('==================display_books_status ===============================================================================================\n')
library.display_books_status()
















print('==================Ajouter_eleve===============================================================================================\n')
