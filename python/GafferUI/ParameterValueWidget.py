##########################################################################
#  
#  Copyright (c) 2011, Image Engine Design Inc. All rights reserved.
#  
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#  
#      * Redistributions of source code must retain the above
#        copyright notice, this list of conditions and the following
#        disclaimer.
#  
#      * Redistributions in binary form must reproduce the above
#        copyright notice, this list of conditions and the following
#        disclaimer in the documentation and/or other materials provided with
#        the distribution.
#  
#      * Neither the name of John Haddon nor the names of
#        any other contributors to this software may be used to endorse or
#        promote products derived from this software without specific prior
#        written permission.
#  
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
#  IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
#  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
#  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#  
##########################################################################

import IECore

import Gaffer
import GafferUI

class ParameterValueWidget( GafferUI.Widget ) :

	def __init__( self, topLevelWidget, parameterHandler ) :
	
		GafferUI.Widget.__init__( self, topLevelWidget )
		
		self.__parameterHandler = parameterHandler
		
		self.__buttonPressConnections = []
	
	def plug( self ) :
	
		return self.__parameterHandler.plug()
		
	def parameter( self ) :
	
		return self.__parameterHandler.parameter()
		
	def parameterHandler( self ) :
	
		return self.__parameterHandler
	
	def _addPopupMenu( self, widget = None, buttons = GafferUI.ButtonEvent.Buttons.Right ) :
	
		if widget is None :
			widget = self
	
		self.__buttonPressConnections.append(
			widget.buttonPressSignal().connect( IECore.curry( Gaffer.WeakMethod( self.__buttonPress ), buttonMask = buttons ) )
		)
	
	## Returns a definition for the popup menu - this is called each time the menu is displayed
	# to allow for dynamic menus. Subclasses may override this method to customise the menu, but
	# should call the base class implementation first.
	def _popupMenuDefinition( self ) :
	
		menuDefinition = IECore.MenuDefinition()
		for name in self.parameter().presetNames() :
			menuDefinition.append( "/" + name, { "command" : IECore.curry( Gaffer.WeakMethod( self.__setValue ), name ) } )

		if len( self.parameter().presetNames() ) :
			menuDefinition.append( "/PresetDivider", { "divider" : True } ) 

		menuDefinition.append( "/Default", { "command" : IECore.curry( Gaffer.WeakMethod( self.__setValue ), self.parameter().defaultValue ) } )

		return menuDefinition
		
	@classmethod
	def create( cls, parameterHandler ) :
	
		parameter = parameterHandler.parameter()
	
		if parameter.presetsOnly :
			return GafferUI.PresetsOnlyParameterValueWidget( parameterHandler )
	
		parameterHierarchy = IECore.RunTimeTyped.baseTypeIds( parameter.typeId() )
		for typeId in [ parameter.typeId() ] + parameterHierarchy :	
			creator = cls.__typesToCreators.get( typeId, None )
			if creator is not None :
				return creator( parameterHandler )
		
		return GafferUI.PlugValueWidget.create( parameterHandler.plug() )
		
	@classmethod
	def registerType( cls, parameterTypeId, creator ) :
	
		cls.__typesToCreators[parameterTypeId] = creator

	__typesToCreators = {}
	
	def __buttonPress( self, widget, event, buttonMask ) :
	
		if event.buttons & buttonMask :
	
			menuDefinition = self._popupMenuDefinition()
			menu = GafferUI.Menu( menuDefinition )
			menu.popup()
			
			return True
			
		return False

	def __setValue( self, value ) :
	
		self.parameter().setValue( value )
		with Gaffer.UndoContext( self.plug().ancestor( Gaffer.ScriptNode.staticTypeId() ) ) :
			self.parameterHandler().setPlugValue()