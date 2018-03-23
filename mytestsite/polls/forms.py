from django import forms

class DeleteForm(forms.Form):
	delete= forms.CharField(label ='delete', max_length=100)
class InsertForm(forms.Form):
	insert= forms.CharField(label ='insert', max_length=100)
class QueryForm(forms.Form):
	query= forms.CharField(label ='Query', max_length=100)
class UpdateForm(forms.Form):
	update= forms.CharField(label ='Update', max_length=100)