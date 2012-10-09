##########################################################################
#  
#  Copyright (c) 2012, John Haddon. All rights reserved.
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
import GafferTest

class ValuePlugTest( GafferTest.TestCase ) :
		
	def testCacheMemoryLimit( self ) :
		
		n = GafferTest.CachingTestNode()
		
		n["in"].setValue( "d" )
		
		v1 = n["out"].getValue( _copy=False )
		v2 = n["out"].getValue( _copy=False )
		
		self.assertEqual( v1, v2 )
		self.assertEqual( v1, IECore.StringData( "d" ) )
		
		# the objects should be one and the same, as the second computation
		# should have shortcut and returned a cached result.
		self.failUnless( v1.isSame( v2 ) )
		
		Gaffer.ValuePlug.setCacheMemoryLimit( 0 )
		
		v3 = n["out"].getValue( _copy=False )
		self.assertEqual( v3, IECore.StringData( "d" ) )

		# the objects should be different, as we cleared the cache.
		self.failIf( v3.isSame( v2 ) )
		
		Gaffer.ValuePlug.setCacheMemoryLimit( self.__originalCacheMemoryLimit )
		
		v1 = n["out"].getValue( _copy=False )
		v2 = n["out"].getValue( _copy=False )
		
		self.assertEqual( v1, v2 )
		self.assertEqual( v1, IECore.StringData( "d" ) )
		
		# the objects should be one and the same, as we reenabled the cache.
		self.failUnless( v1.isSame( v2 ) )
		
	def setUp( self ) :
	
		self.__originalCacheMemoryLimit = Gaffer.ValuePlug.getCacheMemoryLimit()
		
	def tearDown( self ) :
	
		Gaffer.ValuePlug.setCacheMemoryLimit( self.__originalCacheMemoryLimit )
		
if __name__ == "__main__":
	unittest.main()